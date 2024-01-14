from fastapi import FastAPI,Response,status
from redis_om import get_redis_connection,HashModel
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
import time,requests
from fastapi.background import BackgroundTasks


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

redisdb = get_redis_connection(
    host="your redis host",
    port=14355,
    password="password",
    decode_responses=True
)

class Order(HashModel):
    product_id: str
    price: float
    fee: int
    total: float
    quantity: int
    status :str
    
    class Meta:
        database: redisdb

def format(pk:int):
    order = Order.get(pk)
    return {
        "id":pk,
        "product_id":order.product_id,
        "price":order.price,
        "fee":order.fee,
        "total":order.total,
        "quantity":order.quantity,
        "status":order.status,
    }

@app.get("/info")
async def read_root():
    return {"Hello": "World"}

@app.delete("/orders/{pk}")
def delete(pk:str):
    if Order.delete(pk):
        return Response(content='{"message": "deleted"}', status_code=status.HTTP_204_NO_CONTENT)
    else:
        return Response(content='{"message": "no record found"}', status_code=status.HTTP_404_NOT_FOUND)

@app.get("/orders")
def all():
    try:
        all_pks_generator = Order.all_pks()
        all_pks = list(all_pks_generator)  # Convert the generator to a list
        print("All PKs:", all_pks)
        return [format(pk) for pk in all_pks]
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}

@app.post("/orders")
async def create(request:Request,backgroundtask:BackgroundTasks):
    body = await request.json()
    req = requests.get("http://127.0.0.1:7000/products/%s" % body['product_id'])
    print("response from product",req)
    if req.status_code!=200:
       return Response(content='{"message": "product number does not exist"}', status_code=status.HTTP_400_BAD_REQUEST) 
    else:
        product = req.json()
        print("request body",body)
        #check stock enough 
        try:
            i_quantity = int(body['quantity'])
        except Exception as e:
            return Response(content=str(e), status_code=status.HTTP_400_BAD_REQUEST) 
        i_balance = product['quantity']-int(body['quantity'])

        if i_balance>=0:
            i_fee=0.1*product['price']
            i_total=1.1*product['price']
            order =  Order(
                product_id=body["product_id"],
                price=product["price"],
                fee=i_fee,
                total=i_total,
                quantity=body["quantity"],
                status="Pending"
            )
            order.save()
            backgroundtask.add_task(order_complete,order)
            return order
        else:
          return Response(content='{"message": "available product not enough"}', status_code=status.HTTP_400_BAD_REQUEST)   

def order_complete(order:Order):
    time.sleep(5)
    order.status="Complete"
    order.save()
    redisdb.xadd("order_event",order.dict(),'*')
    
