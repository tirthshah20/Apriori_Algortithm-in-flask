import pandas as pd
import numpy as np
from apyori import apriori
from flask import * 
from flask_wtf import Form
from wtforms import TextField
#import upload from flask import * 

path="/Users/tirthshah/Desktop/tirthcsv/"
app = Flask(__name__) 

@app.route('/')  
def upload1():  
    return render_template("file_upload_form.html")

@app.route('/success', methods = ['POST','GET'])  
def success():  
    if request.method == 'POST':  
        f = request.files['file']  
        df=pd.read_csv(f,parse_dates=['Date'])
        all_products = df['itemDescription'].unique()
        one_hot = pd.get_dummies(df['itemDescription'])
        df.drop('itemDescription', inplace=True, axis=1)
        df = df.join(one_hot)
        records = df.groupby(["Member_number","Date"])[all_products[:]].apply(sum)
        records = records.reset_index()[all_products]
        ## Replacing non-zero values with product names
        def get_Pnames(x):
            for product in all_products:
                if x[product] > 0:
                    x[product] = product
            return x
        records = records.apply(get_Pnames, axis=1)  
        x = records.values
        x = [sub[~(sub == 0)].tolist() for sub in x if sub[sub != 0].tolist()]
        transactions = x
        min_supp = request.form['min_support']
        min_conf = request.form['min_confidance']
        min_li = request.form['min_lift']

        rules = apriori(transactions,min_support=float(min_supp),min_confidance=float(min_conf),min_lift=int(min_li),min_length=2,target="rules")
        association_results = list(rules)  
        output = pd.DataFrame(columns=('Items','Antecedent','Consequent','Support','Confidence','Lift'))
        Support =[]
        Confidence = []
        Lift = []
        Items = []
        Antecedent = []
        Consequent=[]
        for RelationRecord in association_results:
            for ordered_stat in RelationRecord.ordered_statistics:
                Support.append(RelationRecord.support)
                Items.append(RelationRecord.items)
                Antecedent.append(ordered_stat.items_base)
                Consequent.append(ordered_stat.items_add)
                Confidence.append(ordered_stat.confidence)
                Lift.append(ordered_stat.lift)
        output['Items'] = list(map(set, Items))                                   
        output['Antecedent'] = list(map(set, Antecedent))
        output['Consequent'] = list(map(set, Consequent))
        output['Support'] = Support
        output['Confidence'] = Confidence
        output['Lift']= Lift 
        output['length'] = output['Antecedent'].apply(lambda x: len(x))
        output.sort_values(by ='length', ascending = False, inplace = True)
        output=output[['Items','Antecedent','Consequent','Support','Confidence','Lift']]  
        output.to_excel('/Users/tirthshah/Downloads/Project/Static/algorithm.xlsx')
        return render_template('file_upload_form.html', items=output.to_dict(orient='records'), columns=output.columns.tolist())

@app.route('/<path:filename>', methods=['GET', 'POST'])

def download(filename):
    return send_from_directory(directory="/Users/tirthshah/Downloads/Project/Static", filename="algorithm.xlsx")  

if __name__ == '__main__':  
    app.run(debug = True) 








