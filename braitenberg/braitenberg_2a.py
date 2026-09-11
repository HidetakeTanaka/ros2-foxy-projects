import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Twist

class Controller_2a(Node):

    def __init__(self) -> None:
        super().__init__("controller_2a")

        # self.count: int = 0
        # self.create_timer(2, self.timer_callback)

        self.create_subscription(
            Float32MultiArray,
            "/computer/color_filter/side_occupancy",
            self.sensor_callback,
            10
        )

        self.velocity_publisher = self.create_publisher(
            Twist,
            "/take/diff_drive_base_controller/cmd_vel_unstamped",
            10
        )

    # def timer_callback(self):
    #     self.get_logger().info(f"Counter: {self.count}")
    #     self.count += 1

    def sensor_callback(self,msg):

        # Get sensor values
        left_sensor = msg.data[0]
        right_sensor = msg.data[1]

        # Vehicle_2a: straight connection
        linear_gain = 2.0
        angular_gain = 10.0
        left_wheel = left_sensor
        right_wheel = right_sensor

        # Convert wheel speeds to Twist
        linear_speed = ((left_wheel + right_wheel) / 2.0) * linear_gain
        angular_speed = (right_wheel - left_wheel) * angular_gain

        # Create velocity command
        cmd = Twist()
        cmd.linear.x = linear_speed
        cmd.angular.z = angular_speed

        # Send command to Foxy
        self.velocity_publisher.publish(cmd)

        self.get_logger().info(
            f"Left: {left_sensor:.2f}, "
            f"Right: {right_sensor:.2f}, "
            f"Linear: {linear_speed:.2f}, "
            f"Angular: {angular_speed:.2f}"
        )


        self.get_logger().info(
            f"Left: {left_sensor:.2f}, Right: {right_sensor:.2f}"
        )

def main(args=None) -> None:

    rclpy.init(args=args)
    node = Controller_2a()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
