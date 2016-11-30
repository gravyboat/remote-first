import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, Markup, make_response
from contextlib import closing
import os
import stripe
from flask.ext.misaka import Misaka
import ast
import datetime
import tweepy
from string import translate, maketrans, punctuation


app = Flask(__name__)
Misaka(app)
app.config.from_object(__name__)

app.config.from_pyfile('remotefirst_settings.cfg', silent=True)

stripe_keys = {
    'secret_key': app.config['SECRET_KEY'],
    'publishable_key': app.config['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def show_ads():
    cur = g.db.execute('select id, companyName, jobTitle,  jobType, publishDate, expirationDate from ads order by id desc')
    ads = [dict(ad_id=row[0], companyName=row[1], jobTitle=row[2], jobType=row[3], publishDate=row[4], expirationDate=row[5]) for row in cur.fetchall()]

    ad_counter = 0
    for ad in ads:
        if (ad['expirationDate'] < datetime.datetime.utcnow().strftime("%Y-%m-%d")):
            ads.pop(ad_counter)
        ad_counter += 1
    return(render_template('index.html', ads=ads))


@app.route('/ad/<id>')
def ad_page(id):
    print(id)
    ad_query = g.db.execute('select jobTitle, jobType, jobDescription, howToApply, companyName, companyURL from ads where id=(?)', (id,))
    ad_details = [dict(jobTitle=row[0], jobType=row[1], jobDescription=row[2],
                       howToApply=row[3], companyName=row[4],
                       companyURL=row[5]
                      ) for row in ad_query.fetchall()]
    for ad in ad_details:
        ad_details = ad
    return(render_template('ad.html', ad_details=ad_details))


@app.route('/search', methods=['POST'])
def search_ad():
    search_items_string = request.form['search_ad']
    search_items = search_items_string.split()
    cur = g.db.execute('select id, companyName, jobTitle,  jobType, jobDescription, publishDate, expirationDate from ads order by id desc')
    ads = [dict(ad_id=row[0], companyName=row[1], jobTitle=row[2], jobType=row[3], jobDescription=row[4], publishDate=row[5], expirationDate=row[6]) for row in cur.fetchall()]
   
    search_results = []
    for ad in ads:
        for item in search_items:
            if item in ad['jobDescription'].lower() or item in ad['jobType'].lower():
                search_results.append(ad)

    ad_counter = 0
    for ad in search_results:
        if (ad['expirationDate'] < datetime.datetime.utcnow().strftime("%Y-%m-%d")):
            search_results.pop(ad_counter)
        ad_counter += 1

    return(render_template('search.html', ads=search_results))


@app.route('/submit', methods=['GET'])
def submit_ad():
    return(render_template('submit.html'))


@app.route('/preview', methods=['POST'])
def preview_ad():
    ad_details = {}
    ad_details['jobTitle'] = request.form['jobTitle']
    ad_details['jobType'] = request.form['jobType']
    ad_details['jobDescription'] = request.form['jobDescription']
    ad_details['howToApply'] = request.form['howToApply']
    ad_details['companyName'] = request.form['companyName']
    ad_details['companyURL'] = request.form['companyURL']
    #job post date details
    print(ad_details)
    return(render_template('preview.html', ad_details=ad_details, key=stripe_keys['publishable_key']))


@app.route('/pay', methods=['POST'])
def pay_ad():
    ad_details = ast.literal_eval(request.form['ad_details'])
    publishDate = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    expirationDate = (datetime.datetime.utcnow() + datetime.timedelta(30)).strftime("%Y-%m-%d")
    ad_details['publishDate'] = publishDate
    ad_details['expirationDate'] = expirationDate
    g.db.execute('insert into ads (jobTitle, jobType, jobDescription, \
                                   howToApply, companyName, companyURL, \
                                   publishDate, expirationDate) \
                                   values (?, ?, ?, ?, ?, ?, ?, ?)',
                                   [ad_details['jobTitle'],
                                    ad_details['jobType'],
                                    ad_details['jobDescription'],
                                    ad_details['howToApply'],
                                    ad_details['companyName'],
                                    ad_details['companyURL'],
                                    ad_details['publishDate'],
                                    ad_details['expirationDate']]
                )
    g.db.commit()

    charge_amount = 5000 # charge amount is in cents
    customer = stripe.Customer.create(
        email = request.form['stripeEmail'],
        card = request.form['stripeToken']
    )

    cur = g.db.execute('select id from ads where jobTitle =(?)', (ad_details['jobTitle'],))
    ad_id_list = [dict(ad_id=row[0]) for row in cur.fetchall()]
    ad_id = ad_id_list[0]
    
    CONSUMER_KEY = app.config['CONSUMER_KEY']
    CONSUMER_SECRET = app.config['CONSUMER_SECRET']
    ACCESS_KEY = app.config['ACCESS_KEY']
    ACCESS_SECRET = app.config['ACCESS_SECRET']

    try:
        charge = stripe.Charge.create(
            customer = customer.id,
            amount = charge_amount,
            currency = 'usd',
            description = 'remote first ad charge'
        )
        
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
        api = tweepy.API(auth)
        api.update_status('{0}: {1}, http://remote-first.com/ad/{2}'.format(ad_details['companyName'],
                                                                            ad_details['jobTitle'],
                                                                            ad_id['ad_id']))
        return(render_template('pay.html', ad_id = ad_id))

    except stripe.CardError, e:
        return """<html><body><h1>Card Declined</h1><p>Your card could not
        be charged. Please check the number and/or contact your credit card
        company.</p></body></html>"""


if __name__ == '__main__':
    app.run()
