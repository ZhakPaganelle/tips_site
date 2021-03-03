import re
import base64
import hashlib
import requests
import pandas as pd
from flask import Flask, jsonify, request, render_template, make_response

TEST_ROOT_LINK = 'https://test.best2pay.net/'
SECTOR = 2532
REFERENCE = 1
DESCRIPTION = 'gratitude'
PASSWORD = 'test'


def renew_db():
    '''
    DB structure:
    receiver_id, login, password, login_signature, name, avatar (link), background (link), qr
    '''

    df = pd.read_csv('db.csv', sep=',')
    df = df.set_index('receiver_id')
    return df


def send_payment(receiver_id, income_sum, outcome_sum):
    params_income = {
        'id': receiver_id,
        'sum': income_sum,
    }
    url_income = ''
    income_req = requests.post(url=url, params=params_income)

    if r.status_code != 200:
        print('Couldn\'t get from payer')
        return

    params_outcome = {
        'id': receiver_id,
        'sum': outcome_sum,
    }
    url_outcome = ''
    income_req = requests.post(url=url, params=params_outcome)

    if r.status_code != 200:
        print('Couldn\'t send to receiver')


def count_comission(payment):
    params = {
        'sum': payment,
    }
    url = ''

    r = requests.post(url=url, params=params)
    return r.text


application = Flask(__name__)


@application.route('/')
def index():
    return render_template('login.html')


@application.route('/register/')
def reg_acc():
    return render_template('register.html')


@application.route('/sign_in/', methods=['POST'])
def sign_in():
    global df

    df = renew_db()

    login = request.form.get('login')
    password = request.form.get('password')

    true_data = False
    
    for receiver_id, person in df.iterrows():
        if person['login'] == login and person['password'] == password:
            return make_response(person['login_signature'])
    return make_response('error')


@application.route('/comp/ooo')
def comp_profile():
    return render_template('company_profile.html')


@application.route('/acc/')
def profile():
    global df

    df = renew_db()
    
    receiver_signature = request.args.get('user')
    usr = None
    
    for receiver_id, person in df.iterrows():
        if person['login_signature'] == receiver_signature:
            usr = person
            break

    name = person['name']
    account_sum = 0

    return render_template('profile.html', name=name, account_sum=account_sum)


@application.route('/new_reg/', methods=['POST'])
def new_reg():
    global df

    df = renew_db()
    
    login = request.form.get('login')
    password = request.form.get('password')
    name = request.form.get('name')
    while 'Ё' in name:
        name = name.replace('Ё', 'Е')
    while 'ё' in name:
        name = name.replace('ё', 'е')
        
    login_signature = get_signature(login)
    
    for receiver_id, person in df.iterrows():
        if person['login_signature'] == login_signature:
            return make_response('error')

    usr_id = len(df)
    client_ref = reg_b2p(name)

    with open('db.csv', 'a', encoding='utf-8') as df:
        df.write(f'{usr_id},{login},{password},{login_signature},{name},{client_ref},default_ava.png,default_back.png,default_qr.png\n')

    return make_response(login_signature)


def reg_b2p(name):
    link = TEST_ROOT_LINK + 'webapi/b2puser/Register'
    first_name, last_name = name.split(' ')
    signature = get_signature(str(SECTOR), first_name, last_name, PASSWORD)

    params = {
        'sector': SECTOR,
        'first_name': first_name,
        'last_name': last_name,
        'signature': signature
        }

    r = requests.post(url=link, params=params)
    client_ref = re.findall(r'<client_ref>(.*)</client_ref>', r.text)[0]
    return client_ref


@application.route('/set_phone/', methods=['post'])
def set_phone():
    login_signature = request.form.get('login_signature')

    for receiver_id, person in df.iterrows():
        if person['login_signature'] == login_signature:
            ref = person['client_ref']
            break
    html_set_phone = set_phone_req(ref)
    print(html_set_phone)


def set_phone_req(client_ref):
    link = TEST_ROOT_LINK + 'webapi/b2puser/SetPhone'
    signature = get_signature(str(SECTOR), client_ref, PASSWORD)

    params = {
        'sector': SECTOR,
        'client_ref': client_ref,
        'signature': signature
        }

    r = requests.post(url=link, params=params)
    return r.text


@application.route('/get_sign_in/', methods=['post'])
def get_sign_in():
    receiver_id = request.form.get('receiver_id')
    amount = request.form.get('payment_sum')

    df = renew_db()

    client_ref = df.at[int(receiver_id), 'client_ref']

    signature = get_signature(str(SECTOR), client_ref, amount, '643', PASSWORD)
    return make_response(signature)

@application.route('/get_client_ref/', methods=['post'])
def get_ref():
    receiver_id = request.form.get('receiver_id')
    
    df = renew_db()
    print(receiver_id)

    client_ref = df.at[int(receiver_id), 'client_ref']

    return make_response(client_ref)


@application.route('/pay_in/', methods=['post'])
def get_gratitude():
    client_ref = request.form.get('client_ref')
    amount = request.form.get('amount')
    fee = request.form.get('fee')

    html_pay_in = pay_in(client_ref, amount, fee)
    print(html_pay_in)


def pay_in(client_ref, amount, fee):
    link = TEST_ROOT_LINK + 'webapi/b2puser/PayIn'
    amount = str(int(float(amount)*100))
    fee = str(int(float(fee)*100))
    signature = get_signature(str(SECTOR), client_ref, amount, '643', PASSWORD)

    params = {
        'sector': SECTOR,
        'amount': amount,
        'fee': fee,
        'to_client_ref': client_ref,
        'signature': signature
        }
    print(link)
    print(params)
    
    r = requests.post(url=link, params=params)
    return r.text


def send_gratitude():
    client_ref = request.form.get('client_ref')
    amount = request.form.get('amount')

    html_pay_out = pay_out(client_ref, amount)
    print(html_pay_out)


def pay_out(client_ref, amount):
    link = TEST_ROOT_LINK + 'webapi/b2puser/PayOut'
    amount = str(int(float(amount)*100))
    signature = get_signature(str(SECTOR), client_ref, amount, '643', PASSWORD)

    params = {
        'sector': SECTOR,
        'amount': amount,
        'from_client_ref': client_ref,
        'signature': signature
        }
    
    r = requests.post(url=link, params=params)
    return r.text
    

@application.route('/comission/', methods=['POST'])
def send_comission():
    value = request.form.get('value')
    comission = get_comission(value)

    return make_response(str(comission))


def get_comission(value):
    comission = 50

    if value:
        comission += int(value) * 0.015
    return comission


@application.route('/input_sum/')
def input_sum():
    global df

    receiver_id = request.args.get('receiver_id')

    df = renew_db()

    name = df.at[int(receiver_id), 'name']
    avatar = df.at[int(receiver_id), 'avatar']
    background = df.at[int(receiver_id), 'background']
    return render_template('copied_initial_page.html', name=name, avatar=avatar, background=background)


@application.route('/users/<receiver_id>')
def user_profile(receiver_id):
    global df

    df = renew_db()

    name = df.at[int(receiver_id), 'name']
    avatar = df.at[int(receiver_id), 'avatar']
    background = df.at[int(receiver_id), 'background']
    qr = df.at[int(receiver_id), 'qr']
    return render_template('user_profile.html', name=name, avatar=avatar, user_background=background, qr=qr,
                           receiver_id=receiver_id)


@application.route('/pay/')
def pay():
    return render_template('card_payment.html')


@application.route('/make_payment/', methods=['POST'])
def make_payment():
    receiver_id = request.form.get('receiver_id')
    receiver_card = df.at[int(receiver_id), 'card']

    value = int(request.form.get('payment_sum'))
    comission_included = request.form.get('comission_included')
    payer_card = request.form.get('card')
    exp = request.form.get('exp')
    exp = exp.replace('/', '')
    cvc = request.form.get('cvc')

    sum_receive = count_income_payment(value, comission_included)
    sum_pay = count_receiver_payment(value, comission_included)

    collect_gratitude(sum_receive, payer_card, exp, cvc)
    pay_gratitude(sum_pay, receiver_card)

    print(receiver_card, value, comission_included, payer_card, exp, cvc)

    return make_response(')')


@application.route('/transfer/', methods=['POST'])
def transfer():
    payment_sum = int(request.form.get('payment_sum'))
    comission_included = int(request.form.get('comission_included'))
    receiver_id = request.form.get('receiver_id')
    card2 = df.at[int(receiver_id), 'card']

    while ' ' in card2:
        card2 = card2.replace(' ', '')

    # Delete
    # card2 = '2200200111114591'
    # Delete

    fee_value = get_comission(payment_sum)
    if comission_included:
        payment_sum -= fee_value

    order_id = register_order(payment_sum)
    print(order_id)
    # , str(order_id)
    transfer_signature = get_signature(str(SECTOR), str(card2), PASSWORD)

    transfer_params = {
        'sector': str(SECTOR),
        # 'id': str(order_id),
        'card2': str(card2),
        'amount': str(int(payment_sum * 100)),
        'fee_value': str(int(fee_value * 100)),
        'signature': transfer_signature
    }
    print(transfer_params)

    transfer_url = TEST_ROOT_LINK + 'webapi/P2PTransfer'
    transfer_req = requests.post(url=transfer_url, params=transfer_params)
    with open('./templates/card_payment_form.html', 'w', encoding='utf-8') as card_payment_form:
        card_payment_form.write(transfer_req.text)

    print(transfer_req.text)

    return make_response(')')


@application.route('/card_payment_form/')
def card_payment_form():
    return render_template('card_payment_form.html')


def register_order(sum_receive):
    register_signature = get_signature(str(SECTOR), str(int(sum_receive) * 100), '643', PASSWORD)

    register_params = {
        'sector': SECTOR,
        'amount': int(sum_receive) * 100,
        'currency': 643,
        'reference': REFERENCE,
        'description': DESCRIPTION,
        'signature': register_signature
    }
    # print(register_params)
    register_url = TEST_ROOT_LINK + 'webapi/Register'
    register_req = requests.post(url=register_url, params=register_params)
    # print(register_req.text)
    order_id = re.findall(r'<id>(.*)</id>', register_req.text)[0]

    return order_id


def get_signature(*args):
    string = (''.join(args)).encode('utf-8')
    m5 = hashlib.md5(string).hexdigest().encode('utf-8')
    signature = base64.b64encode(m5).decode('utf-8')

    return signature


def count_income_payment(value, comission_included):
    if comission_included:
        return value

    comission = get_comission(value)
    value += comission

    return value


def count_receiver_payment(value, comission_included):
    if not comission_included:
        return value

    comission = get_comission(value)
    value -= comission

    return value


if __name__ == '__main__':
    df = renew_db()
    application.run()
