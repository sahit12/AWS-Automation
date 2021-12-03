import pprint
import boto3
import json
import sys
from decimal import Decimal
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError


class Modeltable(object):
    def __init__(self, table, url=None) -> None:
        if not url:
            self.client = boto3.resource(
                'dynamodb', endpoint_url='http://localhost:8000')
        else:
            self.client = boto3.resource('dynamodb')
        self.table = self.client.Table('Movies')

    def create_table(self, tablename, **kwargs):
        try:
            response = self.client.create_table(
                TableName=tablename,
                KeySchema=[
                    {
                        'AttributeName': 'year',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'title',
                        'KeyType': 'RANGE'  # Sort key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'year',
                        'AttributeType': 'N'
                    },
                    {
                        'AttributeName': 'title',
                        'AttributeType': 'S'
                    },
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
            return response
        except ClientError as e:
            print(e)

    def describe_table(self, tablename):
        try:
            client = boto3.client(
                'dynamodb', endpoint_url='http://localhost:8000')
            response = client.describe_table(
                TableName=tablename
            )
            return response
        except ClientError as e:
            print(e)

    def put_data(self, json_data: list):
        try:
            for _it in json.loads(json_data, parse_float=Decimal):
                if not 'year' in _it and not 'title' in _it:
                    print('Please provide the "year" and "title" in the json_data.')
                    sys.exit(0)
                year = int(_it['year'])
                title = _it['title']
                print(f'Putting movie {title}, {year}')
                self.table.put_item(
                    Item=_it
                )
        except ClientError as e:
            print(e)
        except Exception as e:
            print(e)

    def get_data(self, year, title):
        try:
            kwargs = {'year': year}
            if title:
                kwargs['title'] = title
            response = self.table.get_item(
                Key=kwargs
            )
            return response
        except ClientError as e:
            print(e)
        except Exception as e:
            print(e)

    def update_data(self, title, year, actors: None or list, rating=None, plot=None):

        update_expression = 'set'
        update_values = {}
        try:
            if rating:
                update_expression += ' info.rating=:r'
                update_values[':r'] = rating
            if plot:
                update_expression += ' info.plot=:p'
                update_values[':p'] = plot
            if actors:
                update_expression += ' info.actors=:a'
                update_values[':a'] = actors
            response = self.table.update_item(
                Key={
                    'year': year,
                    'title': title
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=update_values,
                ReturnValues='UPDATED_NEW'
            )
            return response
        except ClientError as e:
            print(e)

    def query(self, year, title_range=None, year_range=None):
        try:
            response = self.table.query(
                ProjectionExpression='#yr, title, info.genres, info.actors',
                ExpressionAttributeNames={"#yr": "year"},
                KeyConditionExpression=Key('year').eq(year) & Key('title').between(title_range[0], title_range[1]),
                FilterExpression=Key('info.rating').gte(Decimal(5.0))
            )
            return response['Items']
        except ClientError as e:
            print(e)

if __name__ == '__main__':

    # print('Creating the table: "Movies"...')
    mt=Modeltable(table = 'Movies')
    # mt.create_table('Movies')
    # print('Table created: "Movies"')

    # filename='./DynamoDb/moviedata.json'
    # print(f'Loading file: {filename} to ingest data..')
    # with open(filename) as ptr:
    #     json_data=ptr.read()

    # # Test data to upload to the Table.
    # test_data=json.dumps(
    #     [
    #         {
    #             'year': 2021,
    #             'title': "Venom: Let There Be Carnage",
    #             'info': {
    #                 'plot': 'Eddie Brock attempts to reignite his career by interviewing serial killer Cletus Kasady, who becomes the host of the symbiote Carnage and escapes prison after a failed execution.',
    #                 'rating': 6.3
    #             }
    #         }
    #     ]
    # )
    # print('Adding the file data to the table: "Movies"')
    # mt.put_data(json_data = json_data)

    # print('Adding a recent movie to the data...')
    # mt.put_data(json_data = test_data)
    # print('Added the recent movie to the data.')

    # print('Getting the recently added data from table "Movies"')
    # response=mt.get_data(2021, 'Venom: Let There Be Carnage')
    # pprint.pprint(response)

    # print('Updating the data...')
    # response=mt.update_data(
    #     title = 'Venom: Let There Be Carnage',
    #     year = 2021,
    #     actors = ['Tom Hardy', 'Woody Harrelson', 'Michelle Williams',
    #         'Naomie Harris', 'Reid Scott', 'Stephen Graham']
    # )
    # pprint.pprint(response)
    year = 2000
    title_range = ('A', 'Z')
    print(f"Get movies from {year} with titles from "
          f"{title_range[0]} to {title_range[1]}")
    movies = mt.query(year, title_range)
    for movie in movies:
        print(f"\n{movie['year']} : {movie['title']}")
        pprint.pprint(movie['info'])