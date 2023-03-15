from flask import Flask, Blueprint, render_template, redirect, url_for, request

increment_balance_blueprint = Blueprint('increment_balance', __name__)

@increment_balance_blueprint.route('/increment_balance', methods=['GET', 'POST'])
def increment_balance():
    balance = int(request.form.get('balance'))
    balance += 100
    return redirect(url_for('home'))