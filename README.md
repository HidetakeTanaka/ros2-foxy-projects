# ROS 2 Foxy Projects

A collection of ROS 2 exercises and small projects developed using the
Foxy Robot platform from EOLab, Hochschule Rhein-Waal.

## Projects

### Drive Square
A ROS 2 Python controller that makes Foxy drive a 1 m × 1 m square in Gazebo.

- Uses `geometry_msgs/msg/Twist` for velocity commands
- Uses odometry to measure travelled distance
- Uses yaw orientation for approximately 90° turns
- Uses Gazebo simulation time

Demo:

![Drive Square Demo](drive_square/square_demo.gif)

## Resources

- Foxy Robot repository: https://github.com/EOLab-HSRW/foxy-robot
- Foxy documentation: https://eolab-hsrw.github.io/foxy-docs/
- Drive Square exercise: https://eolab-hsrw.github.io/foxy-docs/docs/exercises/square
