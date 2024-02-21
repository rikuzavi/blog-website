import random
import smtplib
import bcrypt
import ast
import sqlite3
from flask import Flask,render_template,request,redirect,session


app=Flask(__name__)
mess='WELCOME'
name=''
p_id=''
app.secret_key = "FOB"

@app.route('/',methods=['POST','GET'])
def home():
    global mess,name,p_id
    conn = sqlite3.connect('python/data.db')
    cur = conn.cursor()
    cur.execute("select post_no,name,title,content,lik from blog")
    blogs= cur.fetchall()
    cur.execute("select * from likes")
    likes= cur.fetchall()
    if 'accid' not in session:
        name=''
        if request.method == "POST":
            mess='login to like'
            post_id = request.form.get('id')
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
            p_id = post_id
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
    return render_template('index.html',mes=mess,name=name,blogs=blogs,post_idd = p_id,likes=likes)



@app.route('/register',methods=['POST','GET'])
def register():
    global mess
    SUBJECT = 'HELLO WORLD BLOG PAGE '
    mes=''
    em_conf=''
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    if 'accid' in session:
        mess='Logout to Register'
        return redirect('/')
    else:
        if request.method == 'POST':
            name=request.form.get('name')
            password=request.form.get('password')
            email = request.form.get('mailid')
            if(name=='' or password==''):
                warn='Field required ! '
            else:
                salt = bcrypt.gensalt()
                new_p = bcrypt.hashpw(password.encode('utf-8'),salt)
                ran=random.randint(11111,99999)
                b = str(ran)[0:2]
                name=(str(name)+b).upper()
                mes+=f'NAME :- {name}\nId :- {ran}\npass :- {password}'
                cur.execute("insert into account values (:id, :n, :p, :em)",
                            {
                                'id': ran,
                                'n': name,
                                'p': new_p,
                                'em': email
                            })
                conn.commit()
                try:
                    sms = smtplib.SMTP('smtp.gmail.com', 587)
                    sms.starttls()
                    sms.login(user="bankofpeoplebop@gmail.com", password="byoofebjsppicrrd")
                    messege = "Subject: {}\n\n acc detail is  {}".format(SUBJECT, mes)
                    sms.sendmail(from_addr="bankofpeoplebop@gmail.com", to_addrs=email, msg=messege)
                    sms.close()
                    em_conf+='Email sent'
                except:
                    em_conf+='Email Not sent'
                mess=f'Registered  Successfully. id : {ran}  {em_conf}'
                return redirect('/')
        else:
            warn='**Remember User Id and Password**'
    return render_template('register.html',mes=warn)



@app.route('/login',methods=['POST','GET'])
def login():
    global mess,name,salt
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
            if(id=='' or password==''):
                warn ='Field Required !'
            else:
                cur.execute(f'select id, pass, name from account where id = {id}')
                record = cur.fetchone()
                if record is None:
                    warn = 'No Account present. Register first!'
                else:
                    record_id, rec_pas, rec_name = record
                    if not bcrypt.checkpw(password.encode('utf-8'), rec_pas):
                        warn = 'Found But wrong Password!'
                    else:
                        mess = 'Login Success'
                        session['accid'] = str(record_id)
                        name = rec_name
                        return redirect('/')
        return render_template('login.html',warn=warn)



m=''
post_no=''
@app.route('/user',methods=['POST','GET'])
def user():
    global m,post_no,mess
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    if 'accid' not in session:
        return "<body style='background-color : black; color : white;'><center><p style='font-size : 80px;'>404  :(</p><h1>Yo ! <br>Developer is not a fool bro.....<br>login to use this page.</h1></center></body>"
    else:
        cur.execute(f'select name from account where id = {session["accid"]}')
        record_name = cur.fetchall()
        rec_name = ''
        for i in record_name:
            for j in i:
                rec_name += j
        name = rec_name
        if request.method == 'POST':
            button = request.form.get('but')
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
                                                    'li': '0'
                                                })
                    conn.commit()
                    m="Post Added Successfully ....."
                    return redirect('/user')
            if button =='deletepost':
                post_no = request.form.get('post_id')
                cur.execute(f"delete from blog where post_no ='{post_no}'")
                cur.execute(f"delete from likes where post_no ='{post_no}'")
                conn.commit()
                m="Post Deleted Successfully ....."
                return redirect('/user')
            if button =='updatepost':
                post_no = request.form.get('up_post_id')
                up_title = (request.form.get('up_title')).upper()
                up_content = request.form.get('up_content')
                cur.execute("UPDATE blog SET title = ?, content = ? WHERE post_no = ?", (up_title, up_content, post_no))
                conn.commit()
                m="Post Updated Successfully ....."
                return redirect('/user')
            if button == 'deleteacc':
                cur.execute(f"delete from blog where id = '{session["accid"]}'")
                cur.execute(f"delete from account where id = '{session["accid"]}'")
                conn.commit()
                session.pop('accid',None)
                mess="WELCOME"
                return redirect('/')
                
        cur.execute(f"select * from blog where name = '{name}'")
        person_data = cur.fetchall()
        data=[]
        for i in person_data:
            data.append(list(i))
        return render_template('user.html',name=name,id=session["accid"],data=data,mess=m,post_id=post_no)

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