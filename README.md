# SegFormer-ROS2 Wrapper

This is a ROS2 wrapper for Vision Transformers for Semantic Segmentation, [SegFormer](https://arxiv.org/abs/2105.15203). We utilize `huggingface` and the `transformers` for the [source of the algorithm](https://huggingface.co/nvidia/segformer-b0-finetuned-ade-512-512). The main idea is for this container to act as a standalone interface and node, removing the necessity to integrate separate packages and solve numerous dependency issues.

*From Paper:* SegFormer has two appealing features: 1) SegFormer comprises a novel hierarchically structured Transformer encoder which outputs multiscale features. It does not need positional encoding, thereby avoiding the interpolation of positional codes which leads to decreased performance when the testing resolution differs from training. 2) SegFormer avoids complex decoders. The proposed MLP decoder aggregates information from different layers, and thus combining both local attention and global attention to render powerful representations. The paper shows that this simple and lightweight design is the key to efficient segmentation on Transformers.


# Installation Guide

## Using Docker Pull
1. Install [Docker](https://www.docker.com/) and ensure the Docker daemon is running in the background.
2. Run ```docker pull shaderobotics/segformer-segmentation:${ROS2_DISTRO}-${MODEL_VERSION}``` we support all ROS2 distributions along with all model versions found in the model version section below.
3. Follow the run commands in the usage section below

## Build Docker Image Natively
1. Install [Docker](https://www.docker.com/) and ensure the Docker daemon is running in the background.
2. Clone this repo with ```git pull https://github.com/open-shade/segformer_segmentation.git```
3. Enter the repo with ```cd segformer_segmentation```
4. To pick a specific model version, edit the `ALGO_VERSION` constant in `/segformer_seg/segformer_seg.py`
5. Build the container with ```docker build . -t [name]```. This will take a while. We have also provided associated `cloudbuild.sh` scripts to build on GCP all of the associated versions.
6. Follow the run commands in the usage section below.

# Model Versions

* ```b0-finetuned-ade-512-512```
* ```b1-finetuned-ade-512-512```
* ```b2-finetuned-cityscapes-1024-1024```
* ```b3-finetuned-cityscapes-1024-1024```
* ```b4-finetuned-cityscapes-1024-1024```
* ```b4-finetuned-ade-512-512```
* ```b5-finetuned-ade-640-640```
* ```b5-finetuned-cityscapes-1024-1024```

More information about these versions can be found in the [paper](https://arxiv.org/abs/2105.15203). Size of the model increases with the number.

## Example Docker Command

```bash
docker pull shaderobotics/segformer-segmentation:foxy-b0-finetuned-ade-512-512
```

# Parameters
This wrapper utilizes 4 optional parameters to modify the data coming out of the published topics as well as the dataset YOLOS utilizes for comparison. Most parameters can be modified during runtime. However, if you wish to use your own dataset, you must pass that parameter in before runtime. If you are unsure how to pass or update parameters before or during runtime, visit the official ROS2 docs [here](https://docs.ros.org/en/foxy/Concepts/About-ROS-2-Parameters.html?highlight=parameters#setting-initial-parameter-values-when-running-a-node).

The supported, *optional* parameters are...

| Name        | Type    | Default | Use                                                                 |
|-------------|---------|---------|---------------------------------------------------------------------|
| pub_image   | Boolean | True   | Enable or disable the pub of the processed image (with bounding boxes)                |
| pub_pixels    | Boolean | True   | Enable or disable the pub of the pixels with associated classification IDs (8-bit image stream)           |
| pub_detections   | Boolean | True    | Enable or disable the publishing of detections (whether or not to send back a string with all detections found)   |    
| pub_masks   | Boolean | True    | Enable or disable the publishing of masks (whether or not to send back a string with all detections found)   |    

You __do not__ need to specify any parameters, unless you wish to modify the defaults.

# Topics

| Name                   | IO  | Type                             | Use                                                               |
|------------------------|-----|----------------------------------|-------------------------------------------------------------------|
| segformer/image_raw       | sub | [sensor_msgs.msg.Image](http://docs.ros.org/en/noetic/api/sensor_msgs/html/msg/Image.html)            | Takes the raw camera output to be processed                       |
 | segformer/image           | pub | [sensor_msgs.msg.Image](http://docs.ros.org/en/noetic/api/sensor_msgs/html/msg/Image.html)            | Outputs the processed image with segmentation on top of the image |
 | segformer/pixels           | pub | [sensor_msgs.msg.Image](http://docs.ros.org/en/noetic/api/sensor_msgs/html/msg/Image.html)            | Outputs each pixel classified with the associated class ID as an 8-bit stream |
| segformer/detections            | pub | [std_msgs.msg.String](http://docs.ros.org/en/api/std_msgs/html/msg/String.html)              | Outputs all detected classes in the image |
| segformer/masks | pub | [sensor_msgs.msg.Image](http://docs.ros.org/en/noetic/api/sensor_msgs/html/msg/Image.html) | Outputs the masks all in one image colorized based on class    |

# Testing / Demo
To test and ensure that this package is properly installed, replace the Dockerfile in the root of this repo with what exists in the demo folder. Installed in the demo image contains a [camera stream emulator](https://github.com/klintan/ros2_video_streamer) by [klintan](https://github.com/klintan) which directly pubs images to the SegFormer node and processes it for you to observe the outputs.

To run this, run ```docker build . -t --net=host [name]```, then ```docker run -t [name]```. Observing the logs for this will show you what is occuring within the container. If you wish to enter the running container and preform other activities, run ```docker ps```, find the id of the running container, then run ```docker exec -it [containerId] /bin/bash```