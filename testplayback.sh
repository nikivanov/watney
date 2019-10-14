BASE_GPIO_PATH=/sys/class/gpio
ON="1"
exportPin()
{
  if [ ! -e $BASE_GPIO_PATH/gpio$1 ]; then
    echo "$1" > $BASE_GPIO_PATH/export
  fi
}
setOutput()
{
  echo "out" > $BASE_GPIO_PATH/gpio$1/direction
}
setOn()
{
  echo "1" > $BASE_GPIO_PATH/gpio$1/value
}
setOff()
{
  echo "0" > $BASE_GPIO_PATH/gpio$1/value
}
# unmute
exportPin 26
setOutput 26
setOn 26
gst-launch-1.0 filesrc location=test.ogg ! oggdemux ! opusdec ! alsasink
setOff 26

