from main import redisdb,Order
import time

key = "refund_event"
group ="payment_group"

try:
    redisdb.xgroup_create(key,group)
except:
    print("group already exist")

while True:
    try:
        results = redisdb.xreadgroup(group,key,{key:'>'},None)
        print(results)
        if results !=[]:
            for result in results:       
                info = result[1][0][1]
                order = Order.get(info["pk"])
                if order:                    
                    order.status= "Refunded"
                    order.save()
    except Exception as e:
        print(str(e))
    time.sleep(1)

