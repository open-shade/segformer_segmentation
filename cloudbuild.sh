declare -a ROS_VERSIONS=( "foxy" "galactic" "humble" "rolling" )

ORGANIZATION="nvidia"
MODEL_NAME="segformer"
declare -a MODEL_VERSIONS=( "b0-finetuned-ade-512-512" "b1-finetuned-ade-512-512" "b2-finetuned-cityscapes-1024-1024" "b3-finetuned-cityscapes-1024-1024" "b4-finetuned-cityscapes-1024-1024" "b4-finetuned-ade-512-512" "b5-finetuned-ade-640-640" "b5-finetuned-cityscapes-1024-1024" )

for VERSION in "${ROS_VERSIONS[@]}"
do
  for MODEL_VERSION in "${MODEL_VERSIONS[@]}"
  do
    ROS_VERSION="$VERSION"
    HF_VERSION="$MODEL_NAME-$MODEL_VERSION"
    TAG="$MODEL_VERSION"
    gcloud builds submit --config cloudbuild.yaml . --substitutions=_ROS_VERSION="$ROS_VERSION",_TAG="$TAG",_MODEL_VERSION="$HF_VERSION",_ORGANIZATION="$ORGANIZATION" --timeout=10000 &
    pids+=($!)
    echo Dispatched "$MODEL_VERSION" on ROS "$ROS_VERSION"
  done
done

for pid in ${pids[*]}; do
  wait "$pid"
done

echo "All builds finished"
