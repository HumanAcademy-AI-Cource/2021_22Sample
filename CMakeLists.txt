cmake_minimum_required(VERSION 2.8.3)
project(aws_detect_text)

find_package(catkin REQUIRED COMPONENTS
  geometry_msgs
  sensor_msgs
  std_msgs
)


catkin_package()

include_directories(
  ${catkin_INCLUDE_DIRS}
)