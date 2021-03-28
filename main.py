from flask import Flask, jsonify, request, make_response
import datetime

def vremya(stroka):  # функция перевода строки в формат даты
    grany = stroka.split('-')
    grany[0] = grany[0].split(':')
    grany[1] = grany[1].split(':')
    h1 = int(grany[0][0])
    m1 = int(grany[0][1])
    h2 = int(grany[1][0])
    m2 = int(grany[1][1])
    k1 = datetime.time(h1, m1)
    k2 = datetime.time(h2, m2)
    return (k1, k2)

def peresechenie(str1, str2): # проверка пересечения двух промежутков дат
    v1 = vremya(str1)
    v2 = vremya(str2)
    fl = False
    if not (v2[0] >= v1[1] or v2[1] <= v1[0]):
        fl = True
    return fl

def proverka_time(time_orders, working_hours): #проверка на пересечение двух списков дат
    fl = False
    for i in time_orders:
        for j in working_hours:
            if peresechenie(i, j):
                fl = True
    return fl

app = Flask(__name__)


couriers_baza = [] # база курьеров
orders_baza = [] # база заказов
zakazy_v_rabote = {} # принятые заказы в работу
pristupil_k_rabote = {} # дублирующий список закзов в работе
srednee_vremya_rayona = {} # ,база по средним значения времени доставки по районам


@app.route('/')  # для тестирования работы сервера
def index():
    return '<h1>Проверка связи</h1>'


@app.route('/user/<name>')  # для тестирования работы сервера и просмотра значений в базах
def user(name):
    a = "<h1>курьеры</h1>"
    a = a + '</br>'
    a = a + str(couriers_baza)
    a = a + "<h1>заказы</h1>"
    a = a + '</br>'
    a = a + str(orders_baza)
    a = a + "<h1>zakazy_v_rabote</h1>"
    a = a + '</br>'
    a = a + str(zakazy_v_rabote)
    a = a + "<h1>pristupil_k_rabote</h1>"
    a = a + '</br>'
    a = a + str(pristupil_k_rabote)
    a = a + "<h1>srednee_vremya_rayona</h1>"
    a = a + '</br>'
    a = a + str(srednee_vremya_rayona)
    return a


@app.route('/couriers/', methods=['POST'])  # тест пункт 1 (готов. Под вопросом формат response)
def couriers_update():
    new_data = request.json
    new_list = new_data['data']
    er = []
    ok = []
    list_keys_couriers = ['courier_id', 'courier_type', 'regions', 'working_hours']
    fl = True
    for key in new_data['data']:
        if (list(key) == list_keys_couriers):
            a = {"id": key['courier_id']}
            ok.append(a)
        else:
            a = {"id": key['courier_id']}
            er.append(a)
            fl = False
    if fl:
        key = "couriers"
        status = 'HTTP 201 Created'
        num = 201
        res = ok
        for i in new_list:
            couriers_baza.append(i)
    else:
        res = {}
        res["couriers"] = er
        key = "validation_error"
        status = 'HTTP 400 Bad Request'
        num = 400
    otvet = {}
    otvet[key] = res
    return status, num, otvet

@app.route('/couriers/<num>', methods=['POST'])  # тест POST(PATH) пункт 2 (Добавить изменение грузоподъемности)
def couriers_path(num):
    durka.append('добавление')
    new_data = request.json
    for key in new_data:
        if key not in  ['courier_type' , 'regions', 'working_hours']:
            status = 'HTTP 400 Bad Request'
            num = 400
            return status, num
    for i in range(len(couriers_baza)):
        if couriers_baza[i]['courier_id'] == int(num):
            for key in new_data:
                couriers_baza[i][key] = new_data[key]
            res = couriers_baza[i]
    status = 'HTTP 200 OK'
    num = 200
    return status, num, res



@app.route('/orders/', methods=['POST'])  # тест пункт 3 (готов))
def orders_update():
    new_data = request.json
    new_list = new_data['data']
    er = []
    ok = []
    list_keys_orders = ['order_id', 'weight', 'region', 'delivery_hours']
    fl = True
    for key in new_data['data']:
        if (list(key) == list_keys_orders):
            a = {"id": key['order_id']}
            ok.append(a)
        else:
            a = {"id": key['order_id']}
            er.append(a)
            fl = False
    if fl:
        key = "orders"
        status = 'HTTP 201 Created'
        num = 201
        res = ok
        for i in new_list:
            orders_baza.append(i)
    else:
        res = {}
        res["orders"] = er
        key = "validation_error"
        status = 'HTTP 400 Bad Request'
        num = 400
    otvet = {}
    otvet[key] = res
    return status, num, otvet

@app.route('/orders/assign', methods=['POST'])  # тест пункт 4
def orders_assign():
    new_data = request.json
    fl = False
    for i in range(len(couriers_baza)):
        if new_data["courier_id"] == couriers_baza[i]["courier_id"]:
            n = i
            fl = True
    if not fl:
        status = 'HTTP 400 Bad Request'
        num = 400
        return status, num
    if couriers_baza[n]["courier_type"] == "foot":
        ves = 10
    elif couriers_baza[n]["courier_type"] == "bike":
        ves = 15
    elif couriers_baza[n]["courier_type"] == "car":
        ves = 50
    region = couriers_baza[n]["regions"]
    working_hours = couriers_baza[n]["working_hours"]
    first_zakaz = True
    for i in range(len(orders_baza)):
        fl_v_rabote = False
        for key in zakazy_v_rabote:
            if orders_baza[i]["region"] in zakazy_v_rabote[key]:
                fl_v_rabote = True
                break
        if fl_v_rabote:
            continue   # заказ в работе
        if not orders_baza[i]["region"] in region:
            continue # курьер не работет в этом районе
        time_orders = orders_baza[i]["delivery_hours"]
        if not proverka_time(time_orders, working_hours):
            continue # курьер не работает в нужные часы
        if orders_baza[i]["weight"] > ves:
            continue #перегруз
        ves = ves - orders_baza[i]["weight"]
        if first_zakaz:
            res = {}
            res["orders"] = []
            zakazy_v_rabote[couriers_baza[n]["courier_id"]] = []
            first_zakaz = False
        zakazy_v_rabote[couriers_baza[n]["courier_id"]].append(orders_baza[i]["order_id"])
        dobavit_zakaz = {}
        dobavit_zakaz['id'] = orders_baza[i]["order_id"]
        res["orders"].append(dobavit_zakaz)
    time_now = datetime.datetime.now()
    time_now = time_now.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    pristupil_k_rabote[couriers_baza[n]["courier_id"]] = time_now
    status = 'HTTP 200 OK'
    num = 200
    res["assign_time"] = time_now
    return status, num,  res


@app.route('/orders/complete', methods=['POST'])  # тест пункт 5
def orders_complete():
    new_data = request.json
    id = new_data["courier_id"]
    order = new_data["order_id"]
    complite_time = new_data["complete_time"]
    if not id in list(zakazy_v_rabote):
        return "HTTP 400 Bad Request", 400
    if not order in zakazy_v_rabote[id]:
        return "HTTP 400 Bad Request", 400
    for i in range(len(couriers_baza)):
        if id == couriers_baza[i]["courier_id"]:
            n = i
    if not "earnings" in couriers_baza[n]:
        couriers_baza[n]["earnings"] = 0
    if couriers_baza[n]["courier_type"] == 'foot':
        c = 2
    elif couriers_baza[n]["courier_type"] == 'foot':
        c = 5
    elif couriers_baza[n]["courier_type"] == 'foot':
        c = 9
    else:
        c = 1 # на случай ошибки. Здесь надо вставить передачу сообщения об ошибке
    couriers_baza[n]["earnings"] += c * 500

    d1 = datetime.datetime.strptime(pristupil_k_rabote[couriers_baza[n]], '%Y-%m-%dT%H:%M:%S.%fZ')
    d2 = datetime.datetime.strptime(complite_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    d = d2 - d1
    d = d.seconds
    pristupil_k_rabote[couriers_baza[n]] = complite_time
    for i in range(len(orders_baza)):
        if id == orders_baza[i]["order_id"]:
            n_ord = i
    if not orders_baza[n_ord]["regions"] in srednee_vremya_rayona:
        srednee_vremya_rayona[orders_baza[n_ord]["regions"]] = []
    srednee_vremya_rayona[orders_baza[n_ord]["regions"]].append(d)
    t = 0
    for i in srednee_vremya_rayona:
        t_rayona = sum(srednee_vremya_rayona[i] / len(srednee_vremya_rayona[i]))
        if t == 0:
            t = t_rayona
        else:
            if t_rayona < t:
                t = t_rayona
    rating = (60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5
    couriers_baza[n]["rating"] = rating
    del(orders_baza[n_ord])
    zakazy_v_rabote[n].remove(order)
    status = 'HTTP 200 OK'
    num = 200
    res = {}
    res["order_id"] = order
    return status, num, res
    # удалить заказ из базы
    # удалить заказ из в работе
    # создать базу среднее время по району
    # посчитать среднее время по району
    # составить рейтинг
    # снять заказ при выполнении работы


@app.route('/couriers/<num>', methods=['GET'])  # тест GET пункт 6 (готов)
def couriers(num):
    for i in couriers_baza:
        if i["courier_id"] == int(num):
            return i

if __name__ == "__main__":
    app.run(debug=True)
