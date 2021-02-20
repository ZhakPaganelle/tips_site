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


def suka():
    print(1)


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
def get_comission():
    value = request.form.get('value')
    comission = 50

    if value:
        comission += int(value)*0.015
    return make_response(str(comission))
            
@app.route('/input_sum/')
def input_sum():
    receiver_id = request.args.get('receiver_id')
    #receiver = df.iloc[[str(receiver_id)]]
    #print(receiver)
    name = df.at[int(receiver_id), 'name']
    card = df.at[int(receiver_id), 'card']
    avatar = df.at[int(receiver_id), 'avatar']
    background = df.at[int(receiver_id), 'background']
    return render_template('copied_initial_page.html', name=name, card=card, avatar=avatar, background=background)

@app.route('/pay/')
def pay():
    # in_full=0 - param 
    return ')'

if __name__ == '__main__':
    df = renew_db()
    #print(df.iloc[[0]])
    app.run()
