ARG ROS_VERSION=humble
FROM shaderobotics/huggingface:${ROS_VERSION}

ARG ROS_VERSION=humble
ENV ROS_VERSION=$ROS_VERSION

ARG ORGANIZATION=thing
ARG MODEL_VERSION=2

ENV MODEL_NAME="$ORGANIZATION"/"$MODEL_VERSION"

WORKDIR /home/shade/shade_ws

# install additional dependencies here
RUN apt update && \
    apt install -y \
      python3-colcon-common-extensions \
      python3-pip \
      ros-${ROS_VERSION}-cv-bridge \
      ros-${ROS_VERSION}-vision-opencv && \
    echo "#!/bin/bash" >> /home/shade/shade_ws/start.sh && \
    echo "source /opt/shade/setup.sh" >> /home/shade/shade_ws/start.sh && \
    echo "source /opt/ros/${ROS_VERSION}/setup.sh" >> /home/shade/shade_ws/start.sh && \
    echo "source ./install/setup.sh" >> ./start.sh && \
    echo "ros2 run <name> <name>" >> /home/shade/shade_ws/start.sh && \
    chmod +x ./start.sh

COPY . ./src/<name>

RUN pip3 install ./src/<name> && \
    : "Install the model" && \
    python3 -c "from transformers import AutoFeatureExtractor; AutoFeatureExtractor.from_pretrained('${MODEL_NAME}')" && \
    colcon build

ENTRYPOINT ["/home/shade/shade_ws/start.sh"]
