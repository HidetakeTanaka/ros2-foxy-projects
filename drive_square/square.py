import rclpy
import math
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class SquareController(Node):

    def __init__(self):
        super().__init__("square_controller")

       # Publish movement commands
        self.velocity_publisher = self.create_publisher(
        Twist,
        "diff_drive_base_controller/cmd_vel_unstamped",
        10
        )
        # /take/diff_drive_base_controller/cmd_vel_unstamped

        # Receive the robot's position and orientation
        self.create_subscription(
        Odometry,
        "diff_drive_base_controller/odom",
        self.odom_callback,
        10
        )

        self.my_msg = Twist()

        # Movement settings
        self.linear_speed = 0.1         # 0.2 was too fast
        self.angular_speed = math.pi / 20        

        self.target_distance = 1.0

        # Time needed for a 90-degree turn:
        # angle / angular speed = (pi / 2) / 0.4
        # self.turn_time = (math.pi / 2) / self.angular_speed 
        # self.turn_counter = 0
        # self.turn_steps = 100

        # Current odometry values
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        
        self.start_x = 0.0
        self.start_y = 0.0
        self.start_yaw = 0.0
        
        self.odom_received = False
        self.movement_started = False

        self.state = "straight"
        self.side = 0

        self.turn_start_time = None

        # Call move_robot every 0.1 seconds
        self.create_timer(0.01, self.move_robot)

    def odom_callback(self, msg):
        # Read the robot's x and y position
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

        # Orientation
        q = msg.pose.pose.orientation

        self.current_yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )

        self.odom_received = True

    def move_robot(self):

        if not self.odom_received:
            print("Waiting for odometry...")
            return

        # Create a new empty command
        self.my_msg = Twist()

        if self.state == "straight":

            # save the starting position once
            if not self.movement_started:
                self.start_x = self.current_x
                self.start_y = self.current_y

                self.movement_started = True

                print(f"Starting side {self.side +1}")

            # Calculate the distance from the staring position
            distance = math.sqrt(
                (self.current_x - self.start_x)**2
            + (self.current_y - self.start_y)**2
            )

            print(f"Distance: {distance:.2f} m")

            if distance < self.target_distance:
                self.my_msg.linear.x = self.linear_speed

            else:
                self.my_msg.linear.x = 0.0

                self.state = "turn"
                self.movement_started = False

                # self.turn_start_time = self.get_clock().now()
                # self.turn_counter = 0

                # Remember when the turn started
                self.turn_start_time = self.get_clock().now()

                # Remember the direction that the robot was facing before the turn
                self.start_yaw = self.current_yaw
                
                print("Side completed")


        elif self.state == "turn":

            current_time = self.get_clock().now()

            elapsed_time = (current_time - self.turn_start_time).nanoseconds / 1_000_000_000

            # How much has the robot turned?
            turned_angle = self.current_yaw - self.start_yaw

            # Fix angle when crossing +pi / -pi
            turned_angle = math.atan2(math.sin(turned_angle),math.cos(turned_angle))

            turned_angle = abs(turned_angle)
            
            print(f"Turning: {math.degrees(turned_angle):.1f} degrees")

            if turned_angle < math.pi/2 and elapsed_time < 10.0:
                self.my_msg.angular.z = self.angular_speed
            
            # if elapsed_time < 10.0:
            #     self.my_msg.angular.z = self.angular_speed

            else:
                self.my_msg.angular.z = 0.0
                self.side += 1
                self.movement_started = False 

                print("Turn completed!")

                if self.side >= 4:
                    self.state = "finished"
                else:
                    self.state = "straight"

            # if self.turn_counter < self.turn_steps:
            #     # positive angular.z means turn left
            #     self.my_msg.angular.z = self.angular_speed
            #     self.turn_counter += 1

            # else:
            #     self.my_msg.angular.z = 0.0
            #     self.side += 1
            #     self.movement_started = False

            #     print("Turn completed!")

            #     if self.side >= 4:
            #         self.state = "finished"
            #     else:
            #         self.state = "straight"


        elif self.state == "finished":

            self.my_msg.linear.x = 0.0
            self.my_msg.angular.z = 0.0

            print("Square completed")

        self.velocity_publisher.publish(self.my_msg)

    def stop_robot(self):
        stop_msg = Twist()
        self.velocity_publisher.publish(stop_msg)


def main(args=None):

    rclpy.init(args=args)

    node = SquareController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
