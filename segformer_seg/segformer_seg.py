import numpy as np
import os
from transformers import AutoFeatureExtractor, SegformerForSemanticSegmentation
import torch
from PIL import Image as PilImage
from palette import ade_palette
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

ALGO_VERSION = os.getenv("MODEL_NAME")

if not ALGO_VERSION:
    ALGO_VERSION = 'nvidia/segformer-b0-finetuned-ade-512-512'


def predict(image: Image):
    feature_extractor = AutoFeatureExtractor.from_pretrained(ALGO_VERSION)
    model = SegformerForSemanticSegmentation.from_pretrained(ALGO_VERSION)

    inputs = feature_extractor(image, return_tensors="pt")

    with torch.no_grad():
        output = model(**inputs)
    
    labels = model.config.id2labels
    return labels, output.logits


class RosIO(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.declare_parameter('pub_image', True)
        self.declare_parameter('pub_pixels', True)
        self.declare_parameter('pub_detections', True)
        self.declare_parameter('pub_masks', True)
        self.image_subscription = self.create_subscription(
            Image,
            '/<name>/sub/image_raw',
            self.listener_callback,
            10
        )

        self.image_publisher = self.create_publisher(
            String,
            '/<name>/pub/image',
            1
        )
    
        self.pixels_publisher = self.create_publisher(
            String,
            '/<name>/pub/pixels',
            1
        )

        self.detection_publisher = self.create_publisher(
            String,
            '/<name>/pub/detections',
            1
        )

        self.mask_publisher = self.create_publisher(
            String,
            '/<name>/pub/mask',
            1
        )

    def listener_callback(self, msg: Image):
        bridge = CvBridge()
        cv_image: np.ndarray = bridge.imgmsg_to_cv2(msg)
        np_image = np.uint8(cv_image)
        converted_image = PilImage.fromarray(np_image, 'RGB')
        labels, logits = predict(converted_image)
        print(f'Predicted Segmentation')

        upsampled_logits = torch.nn.functional.interpolate(logits,
                                                size=np_image.size[::-1],  # (height, width)
                                                mode='bilinear',
                                                align_corners=False)

        # Second, apply argmax on the class dimension
        seg = upsampled_logits.argmax(dim=1)[0]
        color_seg = np.zeros((seg.shape[0], seg.shape[1], 3), dtype=np.uint8)  # height, width, 3
        palette = np.array(ade_palette())
        for label, color in enumerate(palette):
            color_seg[seg == label, :] = color
            
        # Convert to BGR
        color_seg = color_seg[..., ::-1]

        if self.get_parameter('pub_pixels').value:
            pixel_output = bridge.cv2_to_imgsmg(seg, encoding="mono8")
            self.pixels_publisher.publish(pixel_output)
    
            
        if self.get_parameter('pub_image').value:
            img = np.uint8(cv_image) * 0.5 + color_seg * 0.5
            img_output = bridge.cv2_to_imgsmg(img)
            self.image_publisher.publish(img_output)

        if self.get_parameter('pub_masks').value:
            mask_output = bridge.cv2_to_imgsmg(color_seg)
            self.mask_publisher.publish(mask_output)
        

        if self.get_parameter('pub_detections').value:
            classes = torch.unique(seg).tolist()
            results = []
            for label in classes:
                results.append(labels[label])
            self.detection_publisher.publish(' '.join(results))

        


def main(args=None):
    print('<name> Started')

    rclpy.init(args=args)

    minimal_subscriber = RosIO()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
