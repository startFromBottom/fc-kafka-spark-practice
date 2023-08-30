import time
import json

import requests

from confluent_kafka import Producer
import proto.book_data_pb2 as pb2

from keywords import book_keywords


class KakaoException(Exception):
    pass


def get_original_data(query: str) -> dict:
    rest_api_key = "your api key"

    url = "https://dapi.kakao.com/v3/search/book"
    res = requests.get(
        url=url,
        headers={
            "Authorization": f"KakaoAK {rest_api_key}"
        },
        params={
            "query": query,
            "size": 50,
            "page": 1
        }
    )
    if res.status_code >= 400:
        raise KakaoException(res.content)

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
        for item in original_data['documents']:
            book = pb2.Book()
            book.title = item['title']
            book.title = item['title']
            book.author = ','.join(item['authors'])
            book.publisher = item['publisher']
            book.isbn = item['isbn']
            book.price = int(item['price'])
            book.publication_date = item['datetime']
            book.source = "kakao"
            print("=====")
            print(book)
            print("=====")
            producer.produce(topic="book", value=book.SerializeToString())
        print(f"keyword({keyword}) 전송 완료!")
        time.sleep(10)
