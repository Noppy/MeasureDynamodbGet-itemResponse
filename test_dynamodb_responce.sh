#/bin/bash

# parameter
profile='default'

# DynamoDB
ResultTable='DynamoDBTestResutlTable'
TestTable='DynamoDBTestTable'
MaxEntryInTable=100000000
NumberOfMesurments=1000
Coefficient=10

#Create DynamoDB tables for this test.
# Result Table
TMP=$(aws --profile "${profile}" --output text dynamodb describe-table \
        --table-name "${ResultTable}" \
        --query 'Table.TableId' 2>/dev/null )

if [[ "A${TMP}" == "A" ]]; then
    echo "Create DynamoDB - ${ResultTable}"
    aws --profile ${profile} dynamodb \
        create-table --table-name "${ResultTable}" \
        --attribute-definitions '[{"AttributeName":"Time","AttributeType": "S"}]' \
        --key-schema '[{"AttributeName":"Time","KeyType": "HASH"}]' \
        --provisioned-throughput '{"ReadCapacityUnits": 5,"WriteCapacityUnits": 5}';
fi

# Test Table
# If this table is exist, delete a table before create one.
TMP=$(aws --profile "${profile}" --output text dynamodb describe-table \
        --table-name "${TestTable}" \
        --query 'Table.TableId' 2>/dev/null )

if [[ "A${TMP}" != "A" ]]; then
    echo "Delete DynamoDB - ${TestTable}"
    aws --profile ${profile} dynamodb \
        delete-table --table-name "${TestTable}";
fi

#wait
while true
do 
    TMP=$(aws --profile "${profile}" --output text dynamodb describe-table \
        --table-name "${TestTable}" \
        --query 'Table.TableId' 2>/dev/null )
    if [[ "A${TMP}" == "A" ]]; then
        break
    fi
    sleep 5
done

echo "Create DynamoDB - ${TestTable}"
aws --profile ${profile} dynamodb \
    create-table --table-name "${TestTable}" \
    --attribute-definitions '[{"AttributeName":"sequenceid","AttributeType": "N"}]' \
    --key-schema '[{"AttributeName":"sequenceid","KeyType": "HASH"}]' \
     --billing-mode 'PAY_PER_REQUEST';

#wait
echo 'wait 30seconds'
sleep 30

#test
./mesure_dynamo.py --profile  ${profile} \
                   --resultdb ${ResultTable}\
                   --testdb   ${TestTable}\
                   --coefficient ${Coefficient}  \
                   --max         ${MaxEntryInTable} \
                   --number      ${NumberOfMesurments};

#complete
echo 'Complete!!!!!!!!!!!!!!!'