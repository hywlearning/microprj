from main import redisdb,Product
import time

key = "order_event"
group ="inventory_group"

try:
    redisdb.xgroup_create(key,group)
except:
    print("group already exist")

while True:
    try:
        results = redisdb.xreadgroup(group,key,{key:'>'},None)
        if results!=[]:
            for result in results:       
                info = result[1][0][1]
                print(info)
                try:
                    product = Product.get(info["product_id"])
                    print("product info",product)                    
                    product.quantity=  product.quantity-int(info["quantity"])
                    if product.quantity>=0:
                        product.save()
                    else:
                        redisdb.xadd('refund_event',info,'*')
                except:
                    redisdb.xadd('refund_event',info,'*')
                    print("add refund event")
    except Exception as e:
        print(str(e))
    time.sleep(1)

'''
['order_event',
   [('1705217846250-0',
      {'pk': '01HM3EER8D580BEQAMQMQR7N3Z', 
       'product_id': '01HM32CT7G4C7GFM68GD9AA99J', 
       'price': '10.0', 'fee': '1', 'total': '11.0',
         'quantity': '1', 'status': 'Complete'})]]
'''

