import requests
import pandas as pd
from flask import Flask, request, render_template


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

@app.route('/pay/')
def pay():
    receiver_id = request.args.get('receiver_id')
    #receiver = df.iloc[[str(receiver_id)]]
    #print(receiver)
    name = df.at[int(receiver_id), 'name']
    card = df.at[int(receiver_id), 'card']
    avatar = df.at[int(receiver_id), 'avatar']
    background = df.at[int(receiver_id), 'background']
    return render_template('copied_initial_page.html', name=name, card=card, avatar=avatar, background=background)

if __name__ == '__main__':
    df = renew_db()
    #print(df.iloc[[0]])
    app.run()
