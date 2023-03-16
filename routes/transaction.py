from flask import Flask, Blueprint, render_template, redirect, url_for, request, session
from classes.account import Account

# Blueprints
update_balance_blueprint = Blueprint('update_balance', __name__)
buy_stock_blueprint = Blueprint('buy_stock', __name__)
sell_stock_blueprint = Blueprint('sell_stock', __name__)

# Updates the Balance of the account (positive amount is deposit and negative is withdraw)
@update_balance_blueprint.route('/update_balance', methods=['GET', 'POST'])
def update_balance():
    username = request.args.get('username')
    acc = Account(username)
    if len(request.form['amount']) > 0:
        amount = float(request.form['amount'])
        # Add money
        if request.form['submit-button'] == 'Increment':
            acc.deposit(amount)
        # Remove money
        else:
            acc.withdraw(amount)
        return render_template('home.html',username=username,b=acc.get_balance(),i=acc.get_invest(), amount=0, stocks=acc.get_stocks(), saved=acc.get_saved())
    amount = 0

# Purchase Stock
@buy_stock_blueprint.route('/buy_stock', methods=['GET', 'POST'])
def buy_stock():

    return redirect(url_for('market'))

# Sell Stock
@sell_stock_blueprint.route('/sell_stock', methods=['GET', 'POST'])
def sell_stock():

    return redirect(url_for('market'))