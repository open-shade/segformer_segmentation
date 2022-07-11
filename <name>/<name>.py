import numpy as np
import os
from transformers import AutoFeatureExtractor, DetrForSegmentation
import torch
from PIL import Image as PilImage
from palette import ade_palette
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose
from std_msgs.msg import String
from cv_bridge import CvBridge

ALGO_VERSION = os.getenv("MODEL_NAME")

if not ALGO_VERSION:
    ALGO_VERSION = '<default here>'


def predict(image: Image):
    feature_extractor = AutoFeatureExtractor.from_pretrained(ALGO_VERSION)
    model = DetrForSegmentation.from_pretrained(ALGO_VERSION)

    inputs = feature_extractor(image, return_tensors="pt")

    with torch.no_grad():
        output = model(**inputs)

    # Convert output to be between 0 and 1
    sizes = torch.tensor([tuple(reversed(image.size))])
    result = feature_extractor.post_process_segmentation(output, sizes)
    
    return result[0]


class RosIO(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.declare_parameter('pub_image', False)
        self.declare_parameter('pub_boxes', True)
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
        converted_image = PilImage.fromarray(np.uint8(cv_image), 'RGB')
        result = predict(converted_image)
        print(f'Predicted Segmentation')

        # This code will change based on the result

        base = torch.zeros(result['masks'].shape[1:])
        for i in range(len(result['labels'])):
            base = base.masked_fill_(result['masks'][i] == 1, result['labels'][i])

        pixels = base.numpy().astype(np.uint8)

        if self.get_parameter('pub_pixels').value:
            pixel_output = bridge.cv2_to_imgsmg(pixels, encoding="mono8")
            self.pixels_publisher.publish(pixel_output)
        
        color_seg = np.zeros((base.shape[0], base.shape[1], 3), dtype=np.uint8)
        color_seg = color_seg[..., ::-1]

        palette = np.array(ade_palette())
        for label, color in enumerate(palette):
            color_seg[base == label, :] = color
            
        if self.get_parameter('pub_image').value:
            img = np.uint8(cv_image) * 0.5 + color_seg * 0.5
            img_output = bridge.cv2_to_imgsmg(img)
            self.image_publisher.publish(img_output)

        if self.get_parameter('pub_masks').value:
            mask_output = bridge.cv2_to_imgsmg(color_seg)
            self.mask_publisher.publish(mask_output)
        

        if self.get_parameter('pub_detections').value:
            result = ' '.join(result['labels'].tolist())
            self.detection_publisher.publish(result)

        


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
