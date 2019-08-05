import yaml
from aiohttp import web


def load_yaml():
    try:
        with open('./repo/plugins.yaml', 'rt') as f:
            data = yaml.load(f)
        return data
    except Exception as e:
        print(e)
        pass

data = load_yaml()

for k, v in data.items():
    del v["pip"]
data2 = load_yaml()


async def check(request):
    peername = request.transport.get_extra_info('peername')
    if peername is not None:
        host, port = peername
        print(host, port)
    data = await request.json()
    print(data)
    return web.json_response(data=dict(latestversion="4.0.0.3"))

async def reload_yaml(request):
    global data, data2

    file = load_yaml()
    for k, v in file.items():
        del v["pip"]
    data = file
    data2 = load_yaml()

    return web.json_response(data=data2)

async def get_list(request):
    print("Request List")
    return web.json_response(data=data)

async def get_package_name(request):
    print("Request Package")
    name = request.match_info.get('plugin_name', None)
    if name in data2:
        package_name = data2[name]["pip"]
    else:
        package_name = None
    return web.json_response(data=dict(package_name=package_name))


app = web.Application()
app.add_routes([
    web.get('/list', get_list),
    web.post('/check', check),
    web.get('/reload', reload_yaml),
    web.get('/get/{plugin_name}', get_package_name)])

web.run_app(app, port=2202)
