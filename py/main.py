import requests
import pandas as pd
from flask import Flask, jsonify, request, render_template, make_response


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
