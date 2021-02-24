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
    receiver_id, card, name, avatar (link), background (link)
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


app = Flask(__name__)


@app.route('/')
def index():
    return 'Home Page'

@app.route('/career/')
def career():
    return 'Career Page'

@app.route('/feedback/')
def feedback():
    return 'Feedback Page'

@app.route('/comission/', methods=['POST'])
def send_comission():
    value = request.form.get('value')
    comission = get_comission(value)
    
    return make_response(str(comission))


def get_comission(value):
    comission = 50

    if value:
        comission += int(value)*0.015
    return comission

            
@app.route('/input_sum/')
def input_sum():
    global df
    
    receiver_id = request.args.get('receiver_id')

    df = renew_db()
    
    name = df.at[int(receiver_id), 'name']
    card = df.at[int(receiver_id), 'card']
    avatar = df.at[int(receiver_id), 'avatar']
    background = df.at[int(receiver_id), 'background']
    return render_template('copied_initial_page.html', name=name, card=card, avatar=avatar, background=background)

@app.route('/pay/')
def pay():
    return render_template('card_payment.html')


@app.route('/make_payment/', methods=['POST'])
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


@app.route('/transfer/', methods=['POST'])
def transfer():    
    payment_sum = int(request.form.get('payment_sum'))
    comission_included = int(request.form.get('comission_included'))
    receiver_id = request.form.get('receiver_id')
    card2 = df.at[int(receiver_id), 'card']

    while ' ' in card2:
        card2 = card2.replace(' ' , '')

    # Delete
    card2 = '2200200111114591'
    # Delete

    fee_value = get_comission(payment_sum)
    if comission_included:
        payment_sum -= fee_value

    order_id = register_order(payment_sum)
    print(order_id)
    transfer_signature = get_signature(str(SECTOR), str(order_id), str(card2), PASSWORD)

    transfer_params = {
        'sector': str(SECTOR),
        'id': int(str(order_id)),
        'card2': str(card2),
        'amount': str(payment_sum),
        'fee_value': str(fee_value),
        'signature': transfer_signature
    }
    print(transfer_params)

    transfer_url = TEST_ROOT_LINK + 'webapi/Purchase'
    transfer_req = requests.post(url=transfer_url, params=transfer_params)
    with open('./templates/card_payment_form.html', 'w', encoding='utf-8') as card_payment_form:
        card_payment_form.write(transfer_req.text)

    print(transfer_req.text)

    return make_response(')')


@app.route('/card_payment_form/')
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
    
        


def collect_gratitude(sum_receive, payer_card, exp, cvc):
    pass


def pay_gratitude(sum_pay, receiver_card):
    pass


if __name__ == '__main__':
    df = renew_db()
    #print(df.iloc[[0]])
    app.run()
