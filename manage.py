# -*- coding:utf-8 -*-
""" commandline script to manage project """

import argparse
import csv
import logging
import os
import random
import time

import pandas as pd
from elasticsearch import Elasticsearch
from faker import Faker

from app.extensions.embedding_cilent import EmbeddingClient


def setup_logging(log_level):
    logging.basicConfig(level=log_level, format='%(asctime)s [%(levelname)s] %(message)s')


mappings = {
    "properties": {
        "sku": {
            "type": "keyword"
        },
        "title": {
            "type": "text"
        },
        "description": {
            "type": "text"
        },
        "embedding": {
            "type": "dense_vector",
            "dims": 512,
            "index": True,
            "similarity": "cosine"
        }
    }
}


def generate_demo_data(count, filepath):
    """ generate demo data """
    now = int(time.time())
    fake = Faker()
    with open(filepath, 'wt', encoding='utf-8') as f:
        writer = csv.DictWriter(f, ['SKU ID', 'Title', 'Description'])
        writer.writeheader()
        for i in range(count):
            data = {
                'SKU ID': 'a' + str(now + i),
                'Title': fake.sentence(nb_words=random.randint(5, 20)),
                'Description': fake.sentence(nb_words=random.randint(20, 30))
            }
            writer.writerow(data)


def create_index():
    logging.info(f'index_name: {index_name}')
    cli = Elasticsearch(hosts=[os.environ.get('ES_HOST')])
    try:
        result = cli.indices.create(
            index=index_name,
            mappings=mappings,
        )
        logging.info(f'Index created. response: {result}')
    except Exception as e:
        logging.exception(f'Failed to create index, error: {e}')


cwd = os.path.abspath(os.getcwd())
# model_path = os.path.join(cwd, 'data', 'models', '1')
index_name = os.environ.get('ES_SEARCH_INDEX')
model_name = os.environ.get('EMBEDDING_SERVICE_HOST_MODEL_NAME')
es_host = os.environ.get('ES_HOST')
embedding_host = os.environ.get('EMBEDDING_SERVICE_HOST')


def ingest_data(file_path):
    logging.info(f'csv file path: {file_path}')

    with open(file_path, 'rt', encoding='utf-8') as f:
        r = csv.DictReader(f)
        tb = []
        for row in r:
            data = dict(
                sku=row['SKU ID'],
                title=row['Title'],
                description=row['Description'],
            )
            tb.append(data)

    dt = pd.DataFrame(tb)
    logging.info(f'Model loaded, start transform...')

    logging.info(f'Start word2vec...')
    cli = EmbeddingClient(host=embedding_host, model_name=model_name, logger=logging.getLogger())
    vectors = cli.predict_many(query_list=list(dt['title']))
    dt['embedding'] = vectors
    logging.info(f'Word2vec finished, total: {len(vectors)}')
    cli = Elasticsearch(hosts=[es_host])
    for i, item in dt.iterrows():
        out = cli.index(id=item.sku, index=index_name, document=item.to_dict())
        logging.info(f'Ingest item, id: {item.sku}, result:{out}')


def main():
    parser = argparse.ArgumentParser(description='Script for project management')
    subparsers = parser.add_subparsers(title='Subcommands', dest='subcommand', help='Available subcommands')
    create_index_paser = subparsers.add_parser('create_index', help='Create elasticsearch index')

    ingest_parser = subparsers.add_parser('ingest', help='Ingest data into elasticsearch')
    ingest_parser.add_argument('--input', required=True, help='Product data file in .csv format')

    generate_fake_data_parser = subparsers.add_parser('generate_fake_data', help='Generate fake data for demo')
    generate_fake_data_parser.add_argument('--output', required=True, help='output file path')
    generate_fake_data_parser.add_argument('--count', type=int, default=20, help='output file path')

    parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)

    try:
        if args.subcommand == 'create_index':
            create_index()
        elif args.subcommand == 'ingest':
            ingest_data(args.input)
        elif args.subcommand == 'generate_fake_data':
            generate_demo_data(count=args.count, filepath=args.output)
        else:
            logging.error('Invalid subcommand selected')
    except Exception as e:
        logging.exception(f'Script failed with error: {e}')


if __name__ == '__main__':
    main()
