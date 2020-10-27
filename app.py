from flask import Flask, render_template
import os, requests, json, pdb
import helpers.ns as NS

app = Flask(__name__)

@app.route('/signupdomain', methods=['GET', 'POST'])
def signup_domain():
    error = None
    response = render_template('signupdomain.html')

    if request.method == 'POST':
      reseller = request.form['reseller']
      domain = request.form['domain']
      email = request.form['email']
      access_token = NS.get_access_token()
      check_reseller = NS.check_reseller(reseller, access_token)
      check_domain = NS.check_domain(domain, access_token)
      add_domain = NS.add_preferred_domain(reseller, domain, access_token)
      response = "<p>You created a new domain</p>"

    return response

@app.route("/adddomain")
def add_domain():
  response = render_template('adddomain.html')
  return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8085, debug=True)