from fastapi import FastAPI,Response,status
from redis_om import get_redis_connection,HashModel
from fastapi.middleware.cors import CORSMiddleware
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

class Product(HashModel):
    name: str
    price: float
    quantity: int
    
    class Meta:
        database: redisdb

def format(pk:int):
    product = Product.get(pk)
    return {
        "id":pk,
        "name":product.name,
        "price":product.price,
        "quantity":product.quantity,
    }


@app.get("/info")
async def read_root():
    return {"Hello": "World"}

@app.post("/products")
def create(product:Product):
    return product.save()
    #return Response(product.save(), status_code=201)


@app.put("/products/{pk}")
def update(pk:str,product:Product):
    productinstance = Product.get(pk)
    if productinstance.pk == pk:
        productinstance.quantity=product.quantity
        productinstance.price=product.price
        productinstance.name=product.name
        return productinstance.save()
        #return Response(content='{"message": "updated"}', status_code=status.HTTP_202_ACCEPTED)
    else:
        return Response(content='{"message": "info not correct"}', status_code=status.HTTP_400_BAD_REQUEST)
        

@app.delete("/products/{pk}")
def delete(pk:str):
    Product.delete(pk)
    return Response(content='{"message": "deleted"}', status_code=status.HTTP_204_NO_CONTENT)

@app.get("/products")
def all():
    try:
        all_pks_generator = Product.all_pks()
        all_pks = list(all_pks_generator)  # Convert the generator to a list
        print("All PKs:", all_pks)
        return [format(pk) for pk in all_pks]
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}
    
@app.get("/products/{pk}")
def all(pk:str):
    try:
        return Product.get(pk)
    except Exception as e:
        print("Error:", e)
        return Response(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)