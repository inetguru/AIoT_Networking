# (선택) ROS 2 talker : 온도 값을 'factory/temperature' 토픽으로 발행한다 (DDS 위에서 동작)
#   브로커가 없다. 같은 네트워크의 노드들이 서로를 '자동으로 발견'한다.
import math
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


class Talker(Node):
    def __init__(self):
        super().__init__("temp_sensor")
        self.pub = self.create_publisher(Float64, "factory/temperature", 10)
        self.create_timer(0.5, self.tick)

    def tick(self):
        msg = Float64()
        msg.data = round(23.5 + 0.4 * math.sin(time.time() / 3), 2)
        self.pub.publish(msg)
        self.get_logger().info(f"발행: {msg.data} ℃")


rclpy.init()
rclpy.spin(Talker())
