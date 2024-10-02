import sys
import pika
import json
import threading
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QTabWidget, QLineEdit, QPushButton

class RabbitMQConsumer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.start_consumer_threads()

    def initUI(self):
        self.setWindowTitle('RabbitMQ Consumer Messages')
        self.setGeometry(100, 100, 800, 600)

        self.tab_widget = QTabWidget()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.tab_widget)

        self.direct_tab = QWidget()
        self.fanout_tab = QWidget()
        self.topic_tab = QWidget()

        self.tab_widget.addTab(self.direct_tab, "Direct")
        self.tab_widget.addTab(self.fanout_tab, "Fanout")
        self.tab_widget.addTab(self.topic_tab, "Topic")

        direct_layout = QVBoxLayout(self.direct_tab)
        fanout_layout = QVBoxLayout(self.fanout_tab)
        topic_layout = QVBoxLayout(self.topic_tab)

        self.direct_list = QListWidget()
        self.fanout_list = QListWidget()
        self.topic_list = QListWidget()

        direct_layout.addWidget(self.direct_list)
        fanout_layout.addWidget(self.fanout_list)
        topic_layout.addWidget(self.topic_list)

        self.direct_filter_label = QLabel("Chave de Roteamento:")
        self.direct_filter_input = QLineEdit()
        self.direct_filter_button = QPushButton("Filtrar")
        self.direct_clear_filter_button = QPushButton("Limpar Filtro")
        direct_filter_layout = QHBoxLayout()
        direct_filter_layout.addWidget(self.direct_filter_label)
        direct_filter_layout.addWidget(self.direct_filter_input)
        direct_filter_layout.addWidget(self.direct_filter_button)
        direct_filter_layout.addWidget(self.direct_clear_filter_button)
        direct_layout.addLayout(direct_filter_layout)

        self.topic_filter_label = QLabel("Padrão de Roteamento:")
        self.topic_filter_input = QLineEdit()
        self.topic_filter_button = QPushButton("Filtrar")
        self.topic_clear_filter_button = QPushButton("Limpar Filtro")
        topic_filter_layout = QHBoxLayout()
        topic_filter_layout.addWidget(self.topic_filter_label)
        topic_filter_layout.addWidget(self.topic_filter_input)
        topic_filter_layout.addWidget(self.topic_filter_button)
        topic_filter_layout.addWidget(self.topic_clear_filter_button)
        topic_layout.addLayout(topic_filter_layout)

        self.direct_filter_button.clicked.connect(self.filter_direct_messages)
        self.direct_clear_filter_button.clicked.connect(self.clear_direct_filter)
        self.topic_filter_button.clicked.connect(self.filter_topic_messages)
        self.topic_clear_filter_button.clicked.connect(self.clear_topic_filter)

        self.direct_stats_label = QLabel()
        self.fanout_stats_label = QLabel()
        self.topic_stats_label = QLabel()
        direct_layout.addWidget(self.direct_stats_label)
        fanout_layout.addWidget(self.fanout_stats_label)
        topic_layout.addWidget(self.topic_stats_label)

        self.update_message_counts()
    
    def update_message_counts(self):
        self.direct_message_count = self.direct_list.count()
        self.fanout_message_count = self.fanout_list.count()
        self.topic_message_count = self.topic_list.count()

        self.direct_stats_label.setText(f"Total de Mensagens: {self.direct_message_count}")
        self.fanout_stats_label.setText(f"Total de Mensagens: {self.fanout_message_count}")
        self.topic_stats_label.setText(f"Total de Mensagens: {self.topic_message_count}")

    def clear_direct_filter(self):
        self.direct_filter_input.clear()
        self.load_all_direct_messages()

    def clear_topic_filter(self):
        self.topic_filter_input.clear()
        self.load_all_topic_messages()

    def add_message(self, exchange_type, body, routing_key=None):
        msg = f"[{exchange_type}] {body.decode()}"
        if routing_key:
            msg += f" (Routing Key: {routing_key})"
        item = QListWidgetItem(msg)
        if exchange_type == 'direct':
            self.direct_list.addItem(item)
        elif exchange_type == 'fanout':
            self.fanout_list.addItem(item)
        elif exchange_type == 'topic':
            self.topic_list.addItem(item)
        self.update_message_counts()

    def log_message(self, exchange_type, body, routing_key=None):
        log_entry = {
            "exchange_type": exchange_type,
            "message": body.decode(),
            "timestamp": datetime.now().isoformat()
        }
        if routing_key is not None:
            log_entry["routing_key"] = routing_key

        with open('message_log.json', 'a') as log_file:
            log_file.write(json.dumps(log_entry) + '\n')
        
        self.add_message(exchange_type, body, routing_key)
    
    def load_all_direct_messages(self):
        self.direct_list.clear()
        with open('message_log.json', 'r') as log_file:
            for line in log_file:
                log_entry = json.loads(line)
                if log_entry['exchange_type'] == 'direct':
                    self.add_message('direct', log_entry['message'].encode(), log_entry.get('routing_key'))
        self.update_message_counts()

    def load_all_topic_messages(self):
        self.topic_list.clear()
        with open('message_log.json', 'r') as log_file:
            for line in log_file:
                log_entry = json.loads(line)
                if log_entry['exchange_type'] == 'topic':
                    self.add_message('topic', log_entry['message'].encode(), log_entry.get('routing_key'))
        self.update_message_counts()

    def filter_direct_messages(self):
        routing_key = self.direct_filter_input.text()
        self.direct_list.clear()
        with open('message_log.json', 'r') as log_file:
            for line in log_file:
                log_entry = json.loads(line)
                if log_entry['exchange_type'] == 'direct' and (routing_key == '' or log_entry.get('routing_key') == routing_key):
                    self.add_message('direct', log_entry['message'].encode(), log_entry.get('routing_key'))
        self.update_message_counts()

    def filter_topic_messages(self):
        routing_pattern = self.topic_filter_input.text()
        self.topic_list.clear()
        with open('message_log.json', 'r') as log_file:
            for line in log_file:
                log_entry = json.loads(line)
                if log_entry['exchange_type'] == 'topic' and (routing_pattern == '' or self.match_routing_pattern(log_entry.get('routing_key', ''), routing_pattern)):
                    self.add_message('topic', log_entry['message'].encode(), log_entry.get('routing_key'))
        self.update_message_counts()

    def callback_direct(self, ch, method, properties, body):
        self.log_message('direct', body, method.routing_key)

    def callback_fanout(self, ch, method, properties, body):
        self.log_message('fanout', body)

    def callback_topic(self, ch, method, properties, body):
        self.log_message('topic', body, method.routing_key)

    def filter_direct_messages(self):
        routing_key = self.direct_filter_input.text()
        if routing_key:
            self.direct_list.clear()
            with open('message_log.json', 'r') as log_file:
                for line in log_file:
                    log_entry = json.loads(line)
                    if log_entry['exchange_type'] == 'direct' and log_entry.get('routing_key') == routing_key:
                        self.add_message('direct', log_entry['message'].encode(), log_entry['routing_key'])
        else:
            self.load_all_direct_messages()

    def filter_topic_messages(self):
        routing_pattern = self.topic_filter_input.text()
        if routing_pattern:
            self.topic_list.clear()
            with open('message_log.json', 'r') as log_file:
                for line in log_file:
                    log_entry = json.loads(line)
                    if log_entry['exchange_type'] == 'topic' and self.match_routing_pattern(log_entry.get('routing_key', ''), routing_pattern):
                        self.add_message('topic', log_entry['message'].encode(), log_entry['routing_key'])
        else:
            self.load_all_topic_messages()

    def match_routing_pattern(self, routing_key, pattern):
        parts = routing_key.split('.')
        pattern_parts = pattern.split('.')
        if len(parts) != len(pattern_parts):
            return False
        for i in range(len(parts)):
            if pattern_parts[i] != '#' and parts[i] != pattern_parts[i]:
                return False
        return True

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
        routing_keys = ['projeto', 'sistemas', 'distribuidos']
        for routing_key in routing_keys:
            channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key=routing_key)
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
        routing_keys = ['sistemas.distribuidos', 'projeto.sistemas', 'projeto.distribuidos']
        for routing_key in routing_keys:
            channel.queue_bind(exchange='topic_logs', queue=queue_name, routing_key=routing_key)
        channel.basic_consume(queue=queue_name, on_message_callback=self.callback_topic, auto_ack=True)
        channel.start_consuming()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    consumer = RabbitMQConsumer()
    consumer.show()
    sys.exit(app.exec_())
