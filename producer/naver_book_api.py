import time
import json

import requests

from confluent_kafka import Producer
import proto.book_data_pb2 as pb2

from keywords import book_keywords


class NaverException(Exception):
    pass


def get_original_data(query: str) -> dict:
    client_id = "your client id"
    client_secret = "your client secret"
    url = "https://openapi.naver.com/v1/search/book.json"

    res = requests.get(
        url=url,
        headers={
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
        },
        params={
            "query": query,
            "display": 100,
            "start": 1,
        }
    )
    if res.status_code >= 400:
        raise NaverException(res.content)

    return json.loads(res.text)


if __name__ == '__main__':

    # kafka configs
    conf = {
        'bootstrap.servers': 'localhost:29092',
    }

    # producer 생성
    producer = Producer(conf)
    topic = "book"

    for keyword in book_keywords:
        original_data = get_original_data(keyword)
        for item in original_data['items']:
            book = pb2.Book()
            # dictionary -> protobuf 변환
            book.title = item['title']
            book.author = item['author']
            book.publisher = item['publisher']
            book.isbn = item['isbn']
            book.price = int(item['discount'])
            book.publication_date = item['pubdate']
            book.source = "naver"
            print("=====")
            print(book)
            print("=====")
            producer.produce(topic="book", value=book.SerializeToString())
        print(f"keyword({keyword}) 전송 완료!")
        time.sleep(3)
        producer.flush()
