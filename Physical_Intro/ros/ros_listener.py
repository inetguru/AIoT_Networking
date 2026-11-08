# (선택) ROS 2 listener : 'factory/temperature' 토픽을 구독한다
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


class Listener(Node):
    def __init__(self):
        super().__init__("temp_monitor")
        self.create_subscription(Float64, "factory/temperature", self.on_msg, 10)
        self.get_logger().info("구독 시작: factory/temperature  (발행자를 DDS 가 자동으로 찾아 준다)")

    def on_msg(self, msg):
        self.get_logger().info(f"수신: {msg.data} ℃")


rclpy.init()
rclpy.spin(Listener())
