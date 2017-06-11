from flask import Flask, flash, redirect, render_template, request, url_for, session
from pymongo import MongoClient

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("search_form.html")

def negate(ch):
    return '-{0}'.format(ch)

@app.route("/search",methods=['POST'])
def search():
	if request.method=='POST':
		search_p=request.form['search_positive']
		search_n=request.form['search_negative']		

		results=dict()
		
		if search_p!='' and search_n!='':
			search_n=search_n.split(" ")
			new_negate_set=map(negate,search_n)
			new_negate_words=' '.join(map(str,new_negate_set))
			search_n=new_negate_words
			data_set=search_p+' '+search_n
			client=MongoClient()
			db=client.email
			collection=db.data
			collection.create_index([("$**","text")])
			for data in collection.find({"$text":{"$search":data_set}},{"$score":{"$meta":"textScore"}}):
				results[str(data.get("subject"))]=str(data.get("content"))
			return render_template('search_results.html',results=results)
		elif search_p!='' and search_n=='':
			data_set=search_p
			client=MongoClient()
	        db=client.email
	        collection=db.data
	        collection.create_index([("$**","text")])
	        for data in collection.find({"$text":{"$search":data_set}},{"$score":{"$meta":"textScore"}}):
	        	results[str(data.get("subject"))]=str(data.get("content"))
			return render_template('search_results.html',results=results)
		else:
			return redirect(url_for("index"))

@app.route("/add",methods=['POST'])
def add_data():
    if request.method == 'POST':
        subject=request.form['subject']
        content=request.form['content']
        
        if subject!='' and content !='':
	        client=MongoClient()
	        db=client.email
	        collection=db.data

	        collection.insert_one({"subject":subject,"content":content});

        	flash('Added!')
        	
        return redirect(url_for("index"))

@app.route("/view",methods=['GET'])
def view_all():
	if request.method == 'GET':

		client=MongoClient()
        db=client.email
        collection=db.data

        results=dict()

        for data in collection.find():
        	 results[str(data.get("subject"))]=str(data.get("content"))

        return render_template("added.html",records=results)

if __name__ == "__main__":
    app.secret_key = 'any random string'

    app.debug = True
    app.run()