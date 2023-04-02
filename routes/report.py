from flask import Flask, Blueprint, render_template, redirect, url_for, request, session, jsonify
from classes.account import Account
import alpaca_trade_api as tradeapi
import classes.config as config
import pymongo
from pymongo import MongoClient
import json
import requests

class Report():
    def __init__(self):
        # Accounts DB
        self.cluster = MongoClient("mongodb+srv://Abhari:Abhari@cluster0.pqgawmw.mongodb.net/?retryWrites=true&w=majority")
        self.db = self.cluster["406-Trades"]
        self.accounts = self.db["Accounts"]

        # Connect to the Alpaca API
        self.api = tradeapi.REST(config.API_KEY, config.SECRET_KEY)
        self.headers = {'APCA-API-KEY-ID': config.API_KEY, 'APCA-API-SECRET-KEY': config.SECRET_KEY}

        # Blueprints
        self.generate_report_blueprint = Blueprint('report', __name__)
        
        # Generate Report for User in session
        @self.generate_report_blueprint.route("/report", methods=['GET', 'POST'])
        def report():
            # Checks if account is logged it or not
            if not ('username' in session and session['username'] is not None and len(session['username']) > 0):
                return redirect(url_for('login'))
            else:
                username=session['username']
                acc = self.accounts.find_one({'username': username})
                return render_template('report.html', acc=acc, i=acc['investments'], b=acc['balance'], stocks=acc['stocks'], saved=acc['saved'])
