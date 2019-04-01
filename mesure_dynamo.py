#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import datetime
import json
import argparse
import random
import boto3



def generate_test_data(arg,conf):
    start = conf['counter']+1
    stop = conf['maxnumber']

    #DynamoDB
    session = boto3.Session(profile_name=arg.profile)
    DYNAMO = session.resource('dynamodb')

    try:
        table = DYNAMO.Table(arg.testdb)
        with table.batch_writer() as batch:

            # insert data
            for i in range(start, stop,1):
                batch.put_item(
                    Item={
                        'sequenceid': i,
                        'Address': 'Address-{}'.format(i),
                        'ItemA': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
                        'ItemB': 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
                        'ItemC': 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC',
                        'ItemD': 'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',
                        'ItemE': 'EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE',

                    }
                )
            print('Completed registration. {}-{}'.format(start,i))
            conf['counter'] = i
            return
    except Exception as error:
        print('error:{}'.format(error))
        raise error

def test_getitem(arg,conf):

    session = boto3.Session(profile_name=arg.profile)
    dynamo = session.client('dynamodb')

    for i in range(0, arg.number):


        try:
            id = random.randint(0,conf['counter'])

            # start to meserment  get_item
            start = time.clock_gettime_ns(time.CLOCK_MONOTONIC)
            res = dynamo.get_item(
                TableName=arg.testdb,
                Key={
                    'sequenceid':{'N': str(id)}
                }
            )
            end = time.clock_gettime_ns(time.CLOCK_MONOTONIC)
            # end to meserment get_item
            delta = end - start
            
            #print(json.dumps(res, indent=2))
            print( 'id={0}:  data={1}:  responce(ms)={2:6.2f}'.format(id, res['Item']['Address']['S'], delta/1000000 ))

            #store result to the result table.
            res = dynamo.put_item(
                TableName=arg.resultdb,
                Item={
                    'Time': {'S': '{0}{1}'.format(time.clock_gettime_ns(time.CLOCK_REALTIME), id)},
                    'Max':  {'N': '{0:d}'.format(conf['maxnumber'])},
                    'Id':   {'N': '{0:d}'.format(id)},
                    'Responce_ms': {'N': '{0:f}'.format(delta/1000000)},
                    'Date': {'S': datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}
                }
            )
        except Exception as error:
            print('id={}: error:{}'.format(id, error))



def _main(arg):
    # Debug message
    print('arg_resultDB={}'.format(arg.resultdb) )
    print('arg_testDB={}'.format(arg.testdb) )

    #Initialize
    conf = {
        "counter": -1,
        "maxnumber": 1
    }
    
    #generate test data and test
    while True:

        conf['maxnumber'] *= arg.coefficient
        if conf['maxnumber'] > arg.max:
            conf['maxnumber'] = arg.max
        
        # Generate test data
        generate_test_data(arg,conf)
        #time.sleep(30)

        #test
        test_getitem(arg,conf)
        print('maxnumber={}'.format(conf['maxnumber']))

        #Check & break
        if conf['maxnumber'] >= arg.max:
            break

    #End
    return


def main():
    parser = argparse.ArgumentParser(
        description='DynamoDB response test tool.')

    parser.add_argument('-r','--resultdb',
        action='store',
        default='DynamoDBTestResutlTable',
        type=str,
        required=False,
        help='dynamodb Table for store results.')

    parser.add_argument('-t','--testdb',
        action='store',
        default='DynamoDBTestTable',
        type=str,
        required=False,
        help='dynamodb Table for test.')

    parser.add_argument('-c','--coefficient',
        action='store',
        default=10,
        type=int,
        required=False,
        help='Coefficients for data amplification.')

    parser.add_argument('-m','--max',
        action='store',
        default=100,
        type=int,
        required=False,
        help='maximum size for test data.')

    parser.add_argument('-n','--number',
        action='store',
        default=100,
        type=int,
        required=False,
        help='Number of measurements.')
    
    parser.add_argument('-p','--profile',
        action='store',
        default='default',
        type=str,
        required=False,
        help='Set awscli profile')

    # Do main
    _main(parser.parse_args())

if __name__ == "__main__":
    sys.exit(main())
