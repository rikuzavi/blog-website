import random
import hashlib
import sqlite3
#blog table
#login table


from flask import Flask,render_template,request,redirect,session


app=Flask(__name__)
mess='WELCOME'
name=''
p_id=''
app.secret_key = "FOB"

@app.route('/',methods=['POST','GET'])
def home():
    global mess,name,p_id
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    if 'accid' not in session:
        name=''
        if request.method == "POST":
            mess='login to like'
            post_id = request.form.get('id')
            print(post_id)
            p_id = post_id
    else:
        cur.execute(f'select name from account where id = {session["accid"]}')
        record_name = cur.fetchall()
        rec_name = ''
        for i in record_name:
            for j in i:
                rec_name += j
        name=rec_name
        if request.method == "POST":
            post_id = request.form.get('id')
            print(post_id)
            p_id = post_id
            conn = sqlite3.connect('data.db')
            cur = conn.cursor()

            cur.execute(f'select name from account where id = {session["accid"]}')
            record_name = cur.fetchall()
            rec_name = ''
            for i in record_name:
                for j in i:
                    rec_name += j
            name = rec_name

            cur.execute(f"select person_liked from likes where post_no = {post_id}")
            person_liked = cur.fetchall()
            person=[]
            for i in person_liked:
                person.append(i[0])
            print(person)
            if name in person:
                print('unlike')
                cur.execute(f"select lik from blog where post_no ='{post_id}'")
                l = cur.fetchall()[0][0]
                new_l = int(l) - 1
                cur.execute(f"update blog set lik='{new_l}' where post_no ='{post_id}'")
                cur.execute(f"delete from likes where post_no = '{post_id}' and person_liked = '{name}'")
                conn.commit()
                mess='unlike'
            else:
                print("liked",post_id)
                cur.execute(f"select lik from blog where post_no ='{post_id}'")
                l=cur.fetchall()[0][0]
                new_l = int(l)+1
                cur.execute(f"update blog set lik='{new_l}' where post_no ='{post_id}'")
                cur.execute(f"insert into likes values({post_id},'{name}')")
                conn.commit()
                mess='liked'
            return redirect('/')


    cur.execute("select post_no,name,title,content,lik from blog")
    blogs= cur.fetchall()
    return render_template('index.html',mes=mess,name=name,blogs=blogs,post_idd = p_id)






@app.route('/register',methods=['POST','GET'])
def register():
    global mess
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    if request.method == 'POST':
        name=request.form.get('name')
        password=request.form.get('password')
        if(name=='' or password==''):
            warn='Field required ! '
        else:
            new_p = hashlib.md5(str(password).encode()).hexdigest()
            ran=random.randint(11111,99999)
            b = str(ran)[0:2]
            name=(str(name)+b).upper()
            cur.execute("insert into account values (:id, :n, :p)",
                        {
                            'id': ran,
                            'n': name,
                            'p': new_p
                        })
            conn.commit()
            mess=f'''Registered  Successfully. id : {ran}    password : {password}'''
            return redirect('/')
    else:
        warn='** REMEMBER < USER ID >  and   <PASSWORD> **'
    return render_template('register.html',mes=warn)

#
# @app.route('/post',methods=['POST','GET'])
# def post():
#     global mess
#     conn = sqlite3.connect('data.db')
#     cur = conn.cursor()
#     if request.method == 'POST':
#         title=(request.form.get('title')).upper()
#         content = request.form.get('content')
#         if(title=='' or content==''):
#             mess='Field required !'
#         else:
#             if "accid" not in session:
#                 mess = 'Not logged in !'
#             else:
#                 id=session["accid"]
#                 cur.execute(f"select name from account where id={id}")
#                 name = cur.fetchall()
#                 nam =''
#                 for i in name:
#                     for j in i:
#                         nam+=j
#                 cur.execute("insert into blog values (:id, :n, :ti, :con, :li)",
#                             {
#                                 'id': id,
#                                 'n': nam,
#                                 'ti': title,
#                                 'con': content,
#                                 'li': ''
#                             })
#                 conn.commit()
#                 mess='Post Added'
#     return redirect('/')

@app.route('/login',methods=['POST','GET'])
def login():
    global mess,name
    warn=''
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    if 'accid' in session:
        mess='Already Logged in !'
        cur.execute(f'select name from account where id = {session["accid"]}')
        record_name = cur.fetchall()
        rec_name = ''
        for i in record_name:
            for j in i:
                rec_name += j
        name=rec_name
        return redirect('/')
    else:
        if request.method=='POST':
            id = request.form.get('id')
            password = request.form.get('password')
            new_p = hashlib.md5(str(password).encode()).hexdigest()
            if(id=='' or password==''):
                warn ='Field Required !'
            else:
                cur.execute(f'select id from account where id = {id}')
                record_id=cur.fetchall()
                cur.execute(f'select pass from account where id = {id}')
                record_pass = cur.fetchall()
                rec_pas = ''
                for i in record_pass:
                    for j in i:
                        rec_pas += j
                cur.execute(f'select name from account where id = {id}')
                record_name = cur.fetchall()
                rec_name = ''
                for i in record_name:
                    for j in i:
                        rec_name += j
                if record_id==[] :
                    warn = 'No Account present Register first !'
                elif str(new_p) != rec_pas:
                    warn = 'Found But wrong Password!'
                else:
                    mess ='Login Success'
                    session['accid']=str(id)
                    name=rec_name
                    return redirect('/')
        return render_template('login.html',warn=warn)


@app.route('/user',methods=['POST','GET'])
def user():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute(f'select name from account where id = {session["accid"]}')
    record_name = cur.fetchall()
    rec_name = ''
    for i in record_name:
        for j in i:
            rec_name += j
    name = rec_name
    if request.method == 'POST':
        button = request.form.get('add')
        if button =='addpost':
            title= (request.form.get('title')).upper()
            content= request.form.get('content')
            if title!='' or content!='':
                id=session["accid"]
                cur.execute("insert into blog values (:postno, :id, :n, :ti, :con, :li)",
                                            {
                                                'postno':None,
                                                'id': id,
                                                'n': name,
                                                'ti': title,
                                                'con': content,
                                                'li': ''
                                            })
                conn.commit()
                return redirect('/user')

    cur.execute(f"select * from blog where name = '{name}'")
    person_data = cur.fetchall()
    data=[]
    for i in person_data:
        data.append(list(i))
    return render_template('user.html',name=name,id=session["accid"],data=data)


@app.route('/logout')
def logout():
    global mess,name
    if 'accid' in session:
        session.pop('accid',None)
        mess='Log out Successful'
        name=''
    else:
        mess='Login First'
    return redirect('/')


if __name__=='__main__':
    app.run(debug=True)