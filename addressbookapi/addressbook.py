from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch
#I used https://elasticsearch-py.readthedocs.io/en/master/api.html to find most es functions
app = Flask(__name__)
portNum=9200
es = Elasticsearch([{'host':'localhost','port':portNum}])
ind='address-book'
dType='contact'
#Indicates what ints are returned when there is an error in the input.
es.indices.create(index=ind, ignore=[400,404])

# GET /contact?pageSize={}&page={}&query{}
@app.route('/contact', methods=['GET'])
def getGen():
    #found how to do this from source(https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request)
    #request.args parses values, I indicate the type they should be stored as, and a default value of 10 item.
    #pageSize is how many results are displayed
    pageSize= request.args.get('pageSize',default=10,type=int)
    #Indicates what the offset is, or which factor of size we index from when displaying the results.
    #I have it defaulted to no offset.
    page= request.args.get('page',default=0,type=int)
    #the default here allows for all results if not specified. 
    query= request.args.get('query',default={"query":{"match_all":{}}})
    #helper function to ease unit testing since this avoids the requests for testing.
    return helpGet(pageSize,page,query)

#helper that takes in the fields following ? in url.    
def helpGet(pageSize,page,query):
    #All logical restrictions are included for testing.
    #pageSize must be greater than zero.
    #pageSize indicates how many results are shown.
    if(pageSize<=0):
        return "error: page size must be greater than zero",400
    #I limit the pageSize to 100 items.
    elif(pageSize>100):
        return "error: page size is too large",400
    #search function of elasticsearch gives all instances of query, including close ids.
    #Page is not allowed to be less than zero.
    if(page<0):
        return "error: page must be greater than zero",400
    out=es.search(index=ind,size=pageSize,from_=pageSize*page,body=query)
    #I used source(https://tryolabs.com/blog/2015/02/17/python-elasticsearch-first-steps/)
    #in order to see the format for this return.
    return jsonify(out['hits']['hits']),200

#GET /contact/{name}
#No need for helper since there's REST handling
@app.route('/contact/<name>', methods=['GET'])
def getNameFunc(name):
    if(name=='' or name is None):
        return "Must have name defined",400
    #Check if the name exists to get.
    if(es.exists(index=ind,doc_type=dType,id=name)):
        return es.get(index=ind,doc_type=dType,id=name),200
    #name isn't in es
    else:
        return "error: name not found",404

#POST /contact
#Post a new name after making sure it isn't already there.
@app.route('/contact', methods=['POST'])
def postFunc():
    #found how to do the request functions from source(https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request)
    #I picked 5 field I believed best fit in this API
    name = request.form['name']
    phoneNumber=request.form.get('phoneNumber')
    email=request.form.get('email')
    address=request.form.get('address')
    bio=request.form.get('bio')
    
    #helper for testing.
    return helpPost(name,phoneNumber,email,address,bio)

#helper for Post function that checks for bounds of each value
def helpPost(name,phoneNumber,email,address,bio):
    #If name is already stored, can't store again.
    if(es.exists(index=ind,doc_type=dType,id=name)):
        return "error: contact name already in use",400
    #Max digits in phone number is 15 min is 8
    body={'name':name,'phoneNumber':phoneNumber,'email':email,'address':address,'bio':bio}
    if(body['phoneNumber'] is not None):
        if(len(body['phoneNumber'])>15 or len(body['phoneNumber'])<8):
            return "error: phone number entered is invalid",400
    #max chars in email is 320 min is 3
    if(body['email'] is not None):
        if(len(body['email'])>320 or len(body['email'])<3):
            return "error: email entered is invalid",400
    #max address is limited to 96
    if(body['address'] is not None):
        if(len(body['address'])>96):
            return "error: address entered is invalid",400
    #max bio lenth is 350 chracters.
    if(body['bio'] is not None):
        if(len(body['bio'])>350):
            return "error: bio entered is invalid",400
    #add contact to list.
    out=es.index(index=ind,doc_type=dType,id=name,body=body)
    return out,200

#DELETE /contact/{name} no helper needed
@app.route('/contact/<name>', methods=['DELETE'])
def delFunc(name):
    #Check if name in es
    if(es.exists(index=ind,doc_type=dType,id=name)):
        #delete contact and print which was deleted.
        es.delete(index=ind,doc_type=dType,id=name)
        return "deleted contact"+name,200
    return "error: name not found",404

#PUT /contact/{name}
@app.route('/contact/<name>', methods=['PUT'])
def putFunc(name):
    body=es.get(index=ind,doc_type=dType,id=name)["_source"]
    #replace field if it contains a value
    phoneNumber=request.form.get('phoneNumber',type=int)
    if(phoneNumber is not None):
        body['phoneNumber']=phoneNumber
    email=request.form.get('email',type=int)
    if(email is not None):
        body['email']=phoneNumber
    address=request.form.get('address',type=int)
    if(address is not None):
        body['address']=phoneNumber
    bio=request.form.get('bio',type=int)
    if(bio is not None):
        body['bio']=phoneNumber
    return helpPut(name,body)


def helpPut(name,body):
    if(not es.exists(index=ind,doc_type=dType   ,id=name)):
        return "error: name not found",404
    #Max digits in phone number is 15
    if(body['phoneNumber'] is not None):
        if(len(body['phoneNumber'])>15 or len(body['phoneNumber'])<8):
            return "error: phone number entered is invalid",400
    #max chars in email is 320
    if(body['email'] is not None):
        if(len(body['email'])>320 or len(body['email'])<3):
            return "error: email entered is invalid",400
    #max address is limited to 96
    if(body['address'] is not None):
        if(len(body['address'])>96):
            return "error: address entered is invalid",400
    #max bio lenth is 350 chracters.
    if(body['bio'] is not None):
        if(len(body['bio'])>350):
            return "error: bio entered is invalid",400
    #update contacts based on changes. syntax from source(https://stackoverflow.com/questions/30598152/how-to-update-a-document-using-elasticsearch-py)
    es.update(index=ind,doc_type=dType,id=name,body={"doc":{"name":name,"phoneNumber":body['phoneNumber'],"email":body['email'],"address":body['address'],"bio":body['bio']}})
    return name+ " is updated",200


if __name__ == "__main__":
    app.run(debug=True,port=8080)
# flask help source(https://hackersandslackers.com/the-art-of-building-flask-routes/)
# max telephone number length is 15 source(https://en.wikipedia.org/wiki/Telephone_numbering_plan)