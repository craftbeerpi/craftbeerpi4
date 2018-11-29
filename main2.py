import asyncio

from core.eventbus import EventBus


async def waiter(event):
    print('waiting for it ...')
    await asyncio.sleep(4)
    print('... got it!')
    event.set()

async def main(loop):
    # Create an Event object.
    event = asyncio.Event()

    # Spawn a Task to wait until 'event' is set.
    #waiter_task = asyncio.create_task(waiter(event))

    waiter_task = loop.create_task(waiter(event))
    print("WAIT FOR EVENT")
    await event.wait()



    # Wait until the waiter task is finished.
    await waiter_task

#loop = asyncio.get_event_loop()
#loop.run_until_complete(main(loop))
#loop.close()


bus = EventBus(None)

def test(**kwargs):
    print("")
    print("------------>  HALLO WILD CARD")
    print("")
    print(hex(id(test)))
    print("BUS",bus)


def test2(**kwargs):
    print("------------> HALLO NAME")



class Name():

    def test(self, **kwargs):
        print("---->OK")
        bus.unregister(self.test)
        print("####################  ID2", hex(id(n.test)))


n = Name()
print("the ID", hex(id(n.test)))
id1 = bus.register("test/#", n.test)
print("the ID2", hex(id(n.test)))

if n.test == n.test:
    print("SAME")
id1 = bus.register("test/#", test)
id2 = bus.register("test/name", test2)

print(id1, id2)



print(hex(id(test2)))

print(bus.get_callbacks("test/name"))

bus.fire("test/name")

bus.fire("test/name")

bus.unregister(test2)

bus.fire("test/name")