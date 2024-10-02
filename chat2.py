import sys
import pika
import json
import threading
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem

class RabbitMQConsumer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.start_consumer_threads()

    def initUI(self):
        self.setWindowTitle('RabbitMQ Consumer Messages')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        
        self.label = QLabel("Mensagens Recebidas:")
        layout.addWidget(self.label)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

    def add_message(self, exchange_type, body):
        msg = f"[{exchange_type}] {body.decode()}"
        item = QListWidgetItem(msg)
        self.list_widget.addItem(item)

    def log_message(self, exchange_type, body, correlation_id):
        log_entry = {
            "exchange_type": exchange_type,
            "message": body.decode(),
            "timestamp": datetime.now().isoformat(),
            "correlation_id": correlation_id
        }
        with open('message_log.json', 'a') as log_file:
            log_file.write(json.dumps(log_entry) + '\n')
        
        # Add the message to the GUI
        self.add_message(exchange_type, body)

    def callback_direct(self, ch, method, properties, body):
        self.log_message('direct', body, properties.correlation_id)
        self.respond_to_producer(ch, properties.correlation_id, f"Received: {body.decode()}")

    def callback_fanout(self, ch, method, properties, body):
        self.log_message('fanout', body, properties.correlation_id)

    def callback_topic(self, ch, method, properties, body):
        self.log_message('topic', body, properties.correlation_id)

    def respond_to_producer(self, channel, correlation_id, response):
        channel.basic_publish(exchange='response_logs', routing_key=correlation_id, body=response)

    def start_consumer_threads(self):
        threading.Thread(target=self.consume_direct, daemon=True).start()
        threading.Thread(target=self.consume_fanout, daemon=True).start()
        threading.Thread(target=self.consume_topic, daemon=True).start()

    def consume_direct(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.1.10'))
        channel = connection.channel()
        channel.exchange_declare(exchange='direct_logs', exchange_type='direct')
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key='sistemas')
        channel.basic_consume(queue=queue_name, on_message_callback=self.callback_direct, auto_ack=True)
        channel.start_consuming()

    def consume_fanout(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.1.10'))
        channel = connection.channel()
        channel.exchange_declare(exchange='logs', exchange_type='fanout')
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange='logs', queue=queue_name)
        channel.basic_consume(queue=queue_name, on_message_callback=self.callback_fanout, auto_ack=True)
        channel.start_consuming()

    def consume_topic(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.1.10'))
        channel = connection.channel()
        channel.exchange_declare(exchange='topic_logs', exchange_type='topic')
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange='topic_logs', queue=queue_name, routing_key='distribuidos')
        channel.basic_consume(queue=queue_name, on_message_callback=self.callback_topic, auto_ack=True)
        channel.start_consuming()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    consumer = RabbitMQConsumer()
    consumer.show()
    sys.exit(app.exec_())