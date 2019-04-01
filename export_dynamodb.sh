#!/bin/sh

#dynamodb
profile='mobilepush'
DynamodbTable='DynamoDBTestResutlTable'
csvfile="${DynamodbTable}.csv"

# export from dynamodb
echo '"Date","NumberOfItems","Responce(ms)"' > ${csvfile}
aws --profile ${profile} --output json dynamodb scan --table-name ${DynamodbTable} | jq -r -c '
        .Items[] | [
            .Date.S,
            .Max.N,
            .Responce_ms.N
        ] | @csv'  >> ${csvfile}
