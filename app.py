"""
docstring
"""
from backend import run
from flask import Flask, render_template, request

## APP
app = Flask(__name__)

@app.route('/') #, methods=['POST']
def home():
    """
    home page
    """
    return render_template("base.html")


@app.route('/map', methods=['GET','POST'])
def geomap():

    if request.method == 'POST':
        # get action
        action = request.form['action']

        if action == "geobalisation" : 
            address_from = request.form.get('from')
            address_to = request.form.get('to')
            print(f"ADDRESS : {address_from}")
            print(f"ADDRESS : {address_to}")
            run(address_from, address_to, log=False)
            return render_template('map.html')

        if action == "geofencing" :
            address_from = request.form.get('from')
            address_to = request.form.get('to')
            #run(address_from, address_to, log=False)
            return render_template('geofencing.html')

    # address_from = "55 Rue du Faubourg Saint-Honoré, 75008 Paris"
    # address_to = "12 Rue Olivier Métra, 75020 Paris"
    # run(address_from, address_to, log=False)
    return render_template("base.html")


if __name__ == "__main__":
    app.run(debug=True)