from flask import Flask,request,jsonify,json,current_app
import requests
from boto3.dynamodb.conditions import Key, Attr
import boto3
import boto.dynamodb
from flasgger import Swagger
from functools import wraps
from flask_responses import json_response


app = Flask(__name__)
dynamodb = boto3.resource('dynamodb')
Swagger(app)

def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function

@app.route('/user/register', methods=['POST'])
def register_users():
    """
    This API is to register new users with SaveSmart App
    ---
    tags:
        - Users
    """
    try:
        request_item = json.loads(request.data)
        print request_item['email']
        table = dynamodb.Table('users')
        if not (check_user('users','email',request_item['email'])):
            table.put_item(Item=request_item)
            return json_response(data={'Success':True,'Message':'User created successfully'},status_code=200)
        else:
            return json_response(data={'Success': False, 'Message': 'User already exists'},status_code=400)
    except Exception as e:
        return json_response(data={'Success': False, 'Message': e.message},status_code=400)

@app.route('/login',methods=['POST'])
def verify_login():
    """
    This API is to authenticate users registered with SaveSmart App
    Authorization in Postman is Basic Auth.
    ---
    tags:
        - Users
    """
    user_table = dynamodb.Table('users')
    print request.authorization.username
    items = user_table.scan(FilterExpression=Attr('email').eq(request.authorization.username) and Attr('password').eq(request.authorization.password))
    if items['Count'] == 1:
        return json_response(data={'Success':True,'Message':'Authenticated user'},status_code=200)
    else:
        return json_response(data={'Success': False, 'Message': 'Invalid user'},status_code=404)

def check_user(tablename,primarykey,value):
    try:
        table = dynamodb.Table(tablename)
        items = table.scan(FilterExpression=Attr(primarykey).eq(value))
        print items['Count']
        if items['Count'] == 1:
            return True
        else:
            return False
    except Exception as e:
        return False

@app.route('/products/add', methods=['POST'])
def add_products():
    """
    This API is to add new products with SaveSmart App
    ---
    tags:
        - Products
    """
    try:
        request_item = json.loads(request.data)
        print request_item['id']
        table = dynamodb.Table('products')
        if not (check_user('products','id',request_item['id'])):
            table.put_item(Item=request_item)
            return json_response(data={'Success':True,'Message':'Product added successfully'},status_code=200)
        else:
            return json_response(data={'Success': False, 'Message': 'Product already exists'},status_code=400)
    except Exception as e:
        return json_response(data={'Success': False, 'Message': e.message},status_code=400)


@app.route('/suppliers/add', methods=['POST'])
def add_suppliers():
    """
    This API is to register new suppliers with SaveSmart App
    ---
    tags:
        - Suppliers
    """
    try:
        request_item = json.loads(request.data)
        print request_item['id']
        table = dynamodb.Table('suppliers')
        if not (check_user('suppliers','id',request_item['id'])):
            table.put_item(Item=request_item)
            return json_response(data={'Success':True,'Message':'Supplier added successfully'},status_code=200)
        else:
            return json_response(data={'Success': False, 'Message': 'Supplier already exists'},status_code=400)
    except Exception as e:
        return json_response(data={'Success': False, 'Message': e.message},status_code=400)

@app.route('/manufacturers/add', methods=['POST'])
def add_manufacturers():
    """
    This API is to add new manufacturers with SaveSmart App
    ---
    tags:
        - Manufacturers
    """
    try:
        request_item = json.loads(request.data)
        print request_item['id']
        table = dynamodb.Table('manufacturers')
        if not (check_user('manufacturers','id',request_item['id'])):
            table.put_item(Item=request_item)
            return json_response(data={'Success':True,'Message':'Manufacturer added successfully'},status_code=200)
        else:
            return json_response(data={'Success': False, 'Message': 'Manufacturer already exists'},status_code=400)
    except Exception as e:
        return json_response(data={'Success': False, 'Message': e.message},status_code=400)

@app.route('/users/list',methods=['GET'])
def get_users():
    """
    This API is used to get list of all users registered with SaveSmart App
    ---
    tags:
    - Users
    """
    try:
        table = dynamodb.Table('users')
        items = table.scan(
            ProjectionExpression="email, phone, fullname"
        )
        return json_response(data={'Success':True,'Message':'Request is successful','Response':items['Items'],'Count': items['Count']},status_code=200)
    except Exception as e:
        return json_response(data={'Success': False, 'Message': e.message}, status_code=400)

@app.route('/suppliers/list',methods=['GET'])
def get_suppliers():
    """
    This API is used to get list of all suppliers registered with SaveSmart App
    ---
    tags:
    - Suppliers
    """
    try:
        table = dynamodb.Table('suppliers')
        items = table.scan()
        return json_response(data={'Success':True,'Message':'Request is successful','Response':items['Items'],'Count': items['Count']},status_code=200)
    except Exception as e:
        return json_response(data={'Success': False, 'Message': e.message}, status_code=400)

@app.route('/manufacturers/list',methods=['GET'])
def get_manufacturers():
    """
    This API is used to get list of all manufacturers registered with SaveSmart App
    ---
    tags:
    - Manufacturers
    """
    try:
        table = dynamodb.Table('manufacturers')
        items = table.scan()
        return json_response(data={'Success':True,'Message':'Request is successful','Response':items['Items'],'Count': items['Count']},status_code=200)
    except Exception as e:
        return json_response(data={'Success': False, 'Message': e.message}, status_code=400)

@app.route('/salesrep/list',methods=['GET'])
def get_salesreps():
    """
    This API is used to get list of all sales representatives registered with SaveSmart App
    ---
    tags:
    - Sales Representatives
    """
    try:
        table = dynamodb.Table('sales_rep')
        items = table.scan()
        return json_response(data={'Success':True,'Message':'Request is successful','Response':items['Items'],'Count': items['Count']},status_code=200)
    except Exception as e:
        return json_response(data={'Success': False, 'Message': e.message}, status_code=400)

@app.route('/product/status/<string:productid>/<string:status>', methods=['PUT'])
def update_sensor_status(productid,status):
    """
    This API is used to Update the product status using product id in products
    ---
    tags:
    - Products
    """
    table = dynamodb.Table('products')
    try:
        table.update_item(
            Key={
                'id': productid
            },
            UpdateExpression="set prodstatus = :status",
            ConditionExpression="id = :id",
            ExpressionAttributeValues={
                ':id': productid,
                ':status': status
            },
            ReturnValues="UPDATED_NEW"
        )
        return json_response(data={'Success':True,'Message':'Record updated successfully'},status_code=200)
    except Exception as e:
        return json_response(data={'Success': False, 'Message': e.message}, status_code=400)

@app.route('/products/list',methods=['GET'])
def get_available_sensorpool():
    """
    This API is used to get all the filter on category/type of products from products
    ---
    tags:
    - Products
    """
    try:
        table = dynamodb.Table('products')
        items = table.scan(
            ProjectionExpression="id, pname, price, image"
        )
        print items['Items']
        return json_response(data={'Success':True,'Message':'Request is successful','Response':items['Items'],'Count': items['Count']},status_code=200)
    except Exception as e:
        return json_response(data={'Success': False, 'Message': e.message}, status_code=400)


@app.route('/product/<string:productID>',methods=['GET'])
def get_sensor_information(productID):
    """
    This API is used to get the product information using product id from Products
    ---
    tags:
    - Products
    """
    try:
        table = dynamodb.Table('products')
        response = table.scan(FilterExpression=Attr('id').eq(productID))
        print(response.get('id'))
        items = response['Items']
        print(items)
        return json_response(data={'Success':True,'Message':'Request is successful','Response':response['Items'],'Count': response['Count']},status_code=200)
    except Exception as e:
        return json_response(data={'Success': False, 'Message': e.message}, status_code=400)

if __name__ == '__main__':
    app.run()