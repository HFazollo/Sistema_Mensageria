import pika
import json
import threading
from datetime import datetime


def log_message(exchange_type, body):
    log_entry = {
        "exchange_type": exchange_type,
        "message": body.decode(),
        "timestamp": datetime.now().isoformat()
    }
    with open('message_log.json', 'a') as log_file:
        log_file.write(json.dumps(log_entry) + '\n')

def callback_direct(ch, method, properties, body):
    print(f" [x] Recebeu {body} de Direct Exchange!")
    log_message('direct', body)

def callback_fanout(ch, method, properties, body):
    print(f" [x] Recebeu {body} de Fanout Exchange")
    log_message('fanout', body)

def callback_topic(ch, method, properties, body):
    print(f" [x] Recebeu {body} de Topic Exchange")
    log_message('topic', body)

def consume_direct():
    connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.1.10'))
    channel = connection.channel()

    channel.exchange_declare(exchange='direct_logs', exchange_type='direct')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key='sistemas')
    channel.basic_consume(queue=queue_name, on_message_callback=callback_direct, auto_ack=True)

    channel.start_consuming()

def consume_fanout():
    connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.1.10'))
    channel = connection.channel()

    channel.exchange_declare(exchange='logs', exchange_type='fanout')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='logs', queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=callback_fanout, auto_ack=True)

    channel.start_consuming()

def consume_topic():
    connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.1.10'))
    channel = connection.channel()

    channel.exchange_declare(exchange='topic_logs', exchange_type='topic')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='topic_logs', queue=queue_name, routing_key='distribuidos')
    channel.basic_consume(queue=queue_name, on_message_callback=callback_topic, auto_ack=True)

    channel.start_consuming()

if __name__ == "__main__":
    print(" [*] Esperando por mensagens. Para sair, pressione CTRL+C")

    direct_thread = threading.Thread(target=consume_direct)
    fanout_thread = threading.Thread(target=consume_fanout)
    topic_thread = threading.Thread(target=consume_topic)

    direct_thread.start()
    fanout_thread.start()
    topic_thread.start()

    direct_thread.join()
    fanout_thread.join()
    topic_thread.join()
