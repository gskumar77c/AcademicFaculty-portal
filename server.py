import psycopg2
from flask import Flask, render_template, redirect, url_for, request,flash
import datetime
import bcrypt
import  state
import mongoengine

gsk = {
    'hod':'hod',
    'deanfa': 'Dean Faculty Affairs',
    'deanaa': 'Dean academic affairs',
    'deanra': 'Dean research',
    'deansa': 'Dean student affairs',
    'adeanfa': 'Assosiate dean faculty affairs',
    'adeanaa': 'Assosiate dean academic affairs',
    'adeanra': 'Assosiate dean research',
    'adeansa': 'Assosiate dean student affairs',
    'dir': 'Director'
}

def global_init():
    mongoengine.register_connection(alias='chor', name='faculty')

try:
    conn = psycopg2.connect(database = "project", user = "postgres", password = "123456789", host = "127.0.0.1", port = "5432")
    print("Opened database successfully")
except:
    print("Error Opening Database")
    exit(0)



app = Flask(__name__)
app.secret_key = "super secret key"


def connectgs():
    return psycopg2.connect(database = "project", user = "postgres", password = "123456789", host = "127.0.0.1", port = "5432")

def get_next_member_id(reqid,pth):
    con = connectgs()
    cur = con.cursor()
    cur1 = con.cursor()
    cur.execute('select * from crossFaculty where facultyId = \'{}\''.format(reqid))
    cur1.execute('select * from HOD where facultyId = \'{}\''.format(reqid))
    # nextmem = "&"
    # pos = "&"
    # path = pth.split('->')
    # raavan = []
    # for srn in path:
    #     raavan.append(gsk[srn])
    # print(raavan)
    # path = raavan
    nextmem = "&"
    pos = "&"
    path = pth.split('$')
    if(cur.rowcount==1):
        num = cur.fetchone()
        position = num[1]
        for i in range(len(path)):
            if(path[i]==position):
                if(i!=len(path)-1):
                    pos = path[i+1]
                    cur.execute('select facultyId from crossFaculty where position = \'{}\''.format(pos))
                    if(cur.rowcount==0):
                        print('no faculty under the position {}'.format(pos))
                        nextmem = "7"
                    else :
                        nextmem = cur.fetchone()
                else :
                    pos = "&"
                    nextmem = ("$")
                break
        cur.close()
    elif(cur1.rowcount==1):
        position = 'HOD'
        position1 = 'hod'
        for i in range(len(path)):
            if(path[i]==position or path[i] == position1):
                if(i!=len(path)-1):
                    pos = path[i+1]
                    cur1.execute('select facultyId from crossFaculty where position = \'{}\''.format(pos))
                    if(cur1.rowcount==0):
                        print('no faculty under the position {}'.format(pos))
                        nextmem = "7"
                    else :
                        nextmem = cur1.fetchone()
                else :
                    pos=""
                    nextmem = ("$")
                break
        cur1.close()
    else :
        pos = path[0]
        if(pos=='HOD' or pos =='hod'):
            cur = con.cursor()
            cur.execute('select department from faculty where id = \'{}\''.format(reqid))
            dept = cur.fetchone()
            print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$', dept)
            cur.execute('select facultyId from HOD where departname = \'{}\''.format(dept[0]))
            if(cur.rowcount==0):
                print('no faculty under the position {}'.format(pos))
                nextmem = "7"
            else :
                nextmem = cur.fetchone()
            cur.close()
        else:
            cur = con.cursor()
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            print(pos)
            cur.execute('select facultyId from crossFaculty where position = \'{}\''.format(pos))
            if(cur.rowcount==0):
                print('no faculty under the position {}'.format(pos))
                nextmem = "7"
            else :
                nextmem = cur.fetchone()
            cur.close()
    con.close()
    return (pos,nextmem[0])

def get_leaves(rows):
    leaves = []
    for i in rows:
        gs = list(i)
        leaves.append(gs)
    return leaves

def my_leave_application_status(fid):
    con = connectgs()
    cur = con.cursor()
    cur.execute('select * from leaves where facultyId = \'{}\' order by (lastupdated) desc'.format(fid))
    rows = cur.fetchall()
    leaves = get_leaves(rows)
    cur.close()
    con.close()
    return leaves


def recieved_leave_applications(fid):
    con = connectgs()
    cur = con.cursor()
    cur.execute("select * from leaves where positionid = \'{}\' and facultyId != positionid order by (lastupdated) ".format(fid))
    rows = cur.fetchall()
    leaves = get_leaves(rows)
    cur.close()
    con.close()
    return leaves

@app.route('/comments',methods=['POST','GET'])
def showcomments():
    lid = ""
    lid = request.args.get('type')
    con = connectgs()
    cur = con.cursor()
    cur.execute('select * from comments where leaveid = {} order by (timeofcomment) desc'.format(lid))
    rows = cur.fetchall()
    cur.close()
    con.close()
    comm = get_leaves(rows)
    return render_template('comments.html',posts=comm)



@app.route('/request',methods=['POST','GET'])
def request_for_leave():
    requestor_id = ""
    no_of_days = 0
    comment = ""
    if request.method == 'POST':
        requestor_id = request.form['id']
        no_of_days = request.form['nm']
        comment = request.form['cm']
        con = connectgs()
        cur = con.cursor()
        cur1 = con.cursor()
        cur2 = con.cursor()
        rpth=''
        cur.execute('select * from crossFaculty where facultyId = \'{}\''.format(requestor_id))
        cur1.execute('select * from hod where facultyId = \'{}\''.format(requestor_id))
        pth = state.getPath()
        cur2.execute('select * from faculty where id = \'{}\''.format(requestor_id))
        faculty_row = cur2.fetchone()
        print(type(faculty_row[1]), type(faculty_row[3]), type(no_of_days), '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        if(int(faculty_row[1]) + int(faculty_row[3]) - int(no_of_days) < 0):
            flash('Number of leaves requested are more than available which are this year -> {}, next year {}'.format(faculty_row[1], faculty_row[3]),'error')
            return redirect(url_for('index'))
        requestingNextLeaves = faculty_row[1] - int(no_of_days)
        if(requestingNextLeaves > 0):
            requestingNextLeaves = 0
        else:
            requestingNextLeaves = abs(requestingNextLeaves)
        if(cur1.rowcount==1 or cur.rowcount==1):
            rpth = 'hod$dir'
            pos = 'dir'
            cur1.execute("select * from crossFaculty where position = 'dir'")
            nextid = cur1.fetchone()[0]
        else :
            #print("$$$$$$$$$$$$$$$$$$$$", pth)
            path = state.getPath().split('->')
            for s in range(len(path)):
                if(s != len(path)-1):
                    rpth = rpth + path[s] + '$'
                else :
                    rpth = rpth + path[s]
            pos,nextid = get_next_member_id(requestor_id,rpth)
       
        if(nextid=="7"):
            flash('can not create leave application may be next member in path doesnot exist','error')
            return redirect(url_for('index'))
        if(nextid=="$"):
            flash('last member in path can not apply for leave','error')
            return redirect(url_for('index'))
        con = connectgs()
        cur = con.cursor()
        cur.execute('select * from leaves where facultyid = \'{}\' and (leavestatus = \'requested\' or leavestatus = \'redirected\')'.format(requestor_id))
        if(cur.rowcount==0):
            cur.execute('insert into leaves values(DEFAULT,\'requested\',\'{}\',\'{}\',\'{}\',\'{}\',now(),\'{}\', {})'.format(requestor_id,pos,nextid,no_of_days,rpth, requestingNextLeaves))
            flash('leave requested successfully','success')
            cur.execute("select * from leaves where leavestatus='requested' and facultyid = '{}' and positionid = '{}' ".format(requestor_id,nextid))
            #add code to include comment
            rvn = cur.fetchone()
            create_comment(rvn[0],requestor_id,'faculty',comment)
        else :
            flash('one leave request is already in pending','success')
        cur.close()
        con.commit()
        con.close()
        return redirect(url_for('index'))
    return redirect(url_for('index'))
    



@app.route("/leavelist",methods=['POST','GET'])
def my_leaves():
    s=""
    if request.method == 'POST':
        s = request.form['id']
    leave = my_leave_application_status(s)
    return render_template('viewmylist.html',posts=leave)

@app.route("/accept",methods=['POST','GET'])
def accept():
    lid = 0
    comment = ""
    if request.method == 'POST':
        lid = int(request.form['id'])
        comment = request.form['cm']
    con = connectgs()
    cur = con.cursor()
    cur.execute('select * from leaves where id = {}'.format(lid))
    row = cur.fetchone()
    cur.execute("select * from faculty where Id = '{}'".format(row[2]))
    note = 0
    row2 = cur.fetchone()
    l = row2[1] - row[5]
    x = row2[3]
    if(l < 0):
        note = abs(l)
        x = row2[3] + l
        l = 0
    
    cur.execute('update leaves set leavestatus = \'accepted\',positionid = \'{}\',lastupdated=now(), note = {} where id = {}'.format(row[2], note, lid))
    cur.execute("update faculty set noOfLeaves = '{}', next_year_leaves = '{}' where Id = '{}'".format(l, x, row[2]))
    cur.close()
    con.commit()
    con.close()
    create_comment(lid,row[4],row[3],comment)
    #leave = recieved_leave_applications(row[4])
    #return render_template('finalforwardlist.html',posts=leave)
    return redirect(url_for('req_leaves'))

@app.route("/reject",methods=['POST','GET'])
def reject():
    lid = 0
    comment = ""
    if request.method == 'POST':
        lid = int(request.form['id'])
        comment = request.form['cm']
    con = connectgs()
    cur = con.cursor()
    cur.execute('select * from leaves where id = {}'.format(lid))
    row = cur.fetchone()
    cur.execute('update leaves set leavestatus = \'rejected\',positionid = \'{}\',lastupdated=now() where id = {}'.format(row[2],lid))
    
    cur.close()
    con.commit()
    con.close()
    create_comment(lid,row[4],row[3],comment)
    return redirect(url_for('req_leaves'))
    #leave = recieved_leave_applications(row[4])
    #return render_template('finalforwardlist.html',posts=leave)


@app.route("/reqleavelist",methods=['POST','GET'])
def req_leaves():
    s=""
    if request.method == 'POST':
        s = request.form['id']
    leave = recieved_leave_applications(s)
    return render_template('reqlistview.html',posts=leave)
 

@app.route("/forward",methods=['POST','GET'])
def forward():
    lid = 0
    comment = ""
    if request.method == 'POST':
        lid = int(request.form['id'])
        comment = request.form['cm']
    con = connectgs()
    cur = con.cursor()
    cur.execute('select * from leaves where id = {}'.format(lid))
    row = cur.fetchone()
    pos,nextmem = get_next_member_id(row[4],row[len(row)-2])
    '''
    print("\n$$$$$$$$$$$$$$$$$$$$$$$\n")
    print(pos,nextmem)
    print("\n$$$$$$$$$$$$$$$$$$$$$$$\n")
    '''
    cntr = 0
    if(nextmem[0]=='$' or nextmem =="$") :
        print('can not forward')
    elif (nextmem[0]=='7' or nextmem == '7') :
        print("path position and member position are not matching","error")
    else :
        cur.execute('update leaves set leavestatus = \'requested\',positionid = \'{}\',position=\'{}\',lastupdated=now() where id = {}'.format(nextmem,pos,lid))
        cntr=1
    cur.close()
    con.commit()
    con.close()
        #return redirect(url_for('leaves',s=row[4]))
    if(row[1]=='redirected'):
        '''
        print("\n$$$$$$$$$$$$$$$$$$$$$$$ fid\n")
        print(row[4])
        print("\n$$$$$$$$$$$$$$$$$$$$$$$\n")
        '''
        if(cntr==1):
            create_comment(lid,row[4],"faculty(me)",comment)
        #leave = my_leave_application_status(row[2])
        #return render_template('viewmylist.html',posts=leave)
        return redirect(url_for('my_leaves'))
    else :
        '''
        print("\n$$$$$$$$$$$$$$$$$$$$$$$ pid\n")
        print(row[4])
        print("\n$$$$$$$$$$$$$$$$$$$$$$$\n")
        '''
        if(cntr==1):
            create_comment(lid,row[4],row[3],comment)
        #leave = recieved_leave_applications(row[4])
        #return render_template('reqlistview.html',posts=leave)
        return redirect(url_for('req_leaves'))


def create_comment(lid,comenterid,pos,s):
    con = connectgs()
    cur = con.cursor()
    cur.execute('insert into comments values({},\'{}\',\'{}\',\'{}\')'.format(lid,s,comenterid,pos))
    cur.close()
    con.commit()
    con.close()


@app.route("/redirect",methods=['POST','GET'])
def redirect_to_sender():
    lid = 0
    comment = ""
    if request.method == 'POST':
        lid = int(request.form['id'])
        comment = request.form['cm']
    con = connectgs()
    cur = con.cursor()
    cur.execute('select * from leaves where id = {}'.format(lid))
    row = cur.fetchone()
    cur.execute('update leaves set leavestatus =\'redirected\',positionid = \'{}\',lastupdated = now() where id = {}'.format(row[2],lid))
    cur.close()
    con.commit()
    con.close()
    create_comment(lid,row[4],row[3],comment)
    #return redirect(url_for('leaves',s=row[4]))
    #leave = recieved_leave_applications(row[4])
    #return render_template('viewmylist.html',posts=leave)
    return redirect(url_for('req_leaves'))

###############################raavan###########################################
###############################ends#############################################



@app.route('/')
@app.route('/home')
def index():
    if(state.active_account != None and state.active_account.email == 'admin@admin.com'):
       return render_template('admin.html', path = state.getPath())
    if(state.active_account != None):
        info = state.getInfo(state.active_account.email)
        
        con = connectgs()
        cur = con.cursor()
        cur1 = con.cursor()
        cur.execute('select * from crossFaculty where facultyId = \'{}\''.format(state.active_account.email))
        cur1.execute('select * from hod where facultyId = \'{}\''.format(state.active_account.email))
        pos = ''
        if(cur.rowcount==1):
            row = cur.fetchone()
            pos = row[1]
        if(cur1.rowcount==1):
            pos = 'hod'
        cur.close()
        cur1.close()
        con.close()
        print('$$$$$$$$$$', pos)
        if(len(pos)):
            return render_template('info.html', info = info, pos = gsk[pos])
        return render_template('info.html', info = info)
    
    else:
        return render_template('login.html')

@app.route('/admin', methods = ['GET', 'POST'])
def admin():
    global path
    if(state.active_account == None or state.active_account.email != 'admin@admin.com'):
        return render_template('login.html')
    if(request.method == 'POST'):
        if 'savePath' in request.form:
            print('###########')
            path = request.form['path'].lower()
            if(len(path) > 0):
                state.changePath(path)
                return render_template('admin.html',path = state.getPath(), status = "path set correctly")
            return render_template('admin.html',path = state.getPath(), error = "length of path should be > 0")
        if 'SetHOD' in request.form:
            if request.form['CHOD'] is None:
                return render_template('admin.html', path = state.getPath(), error1='Need Department')
            email = request.form['newHOD']
            if state.find_account_by_email(email) is None:
                return render_template('admin.html', path = state.getPath(), error1='Faculty Not present')
            conn = connectgs()
            cur = conn.cursor()
            cur.execute("select position from crossfaculty where facultyid = \'%s\'" % (str(email)))
            data = cur.fetchone()
            if data is not None:
                return render_template('admin.html', path = state.getPath(), error1='Faculty Already a Cross Faculty')
            
            dept = str(request.form['CHOD'])
            eid = str(email)
            '''
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\n")
            print(dept,eid)
            print("$$$$$$$$$$$$$$$$$$$$$$$########\n")
            '''
            if state.find_account_by_email(email).Department != dept:
                return render_template('admin.html', path = state.getPath(), error1='Faculty Should be of same department')
            #cur.execute("select changeHod(%s, %s)", (str(dept), str(email)))
            
            cur.execute("select changeHod(%s, %s)", (dept, email))
            #cur.execute("select changeHod('{}', '{}')".format(str(request.form['CHOD']), str(email)))
            cur.close()
            conn.commit()
            conn.close()
            return render_template('admin.html', path = state.getPath(), status1='HOD updated Succesfully')
        if 'SetDEAN' in request.form:
            if request.form['CDEAN'] is None:
                return render_template('admin.html',path = state.getPath(), error2='Need Department')
            email = request.form['newDEAN']
            if state.find_account_by_email(email) is None:
                return render_template('admin.html', path = state.getPath(), error2='Faculty Not present')
            conn = connectgs()
            cur = conn.cursor()
            cur.execute("select position from crossfaculty where facultyid = \'%s\'" % (str(email)))
            data = cur.fetchone()
            if data is not None:
                return render_template('admin.html', path = state.getPath(), error2='Faculty Already a Cross Faculty')
            
            dept = str(request.form['CDEAN'])
            email = str(email)
            cur.execute("select changeCross(%s, %s)", (dept, email))
            cur.close()
            conn.commit()
            conn.close()
            return render_template('admin.html', status2 = 'Dean updated successfully', path = state.getPath())
        if 'SetDIR' in request.form:
            email = request.form['newDIR']
            if state.find_account_by_email(email) is None:
                return render_template('admin.html', path = state.getPath(),  error3='Faculty Not present')
            conn = connectgs()
            cur = conn.cursor()
            cur.execute("select position from crossfaculty where facultyid = \'%s\'" %(str(email)))
            data = cur.fetchone()
            if data is not None:
                return render_template('admin.html', path = state.getPath(), error3='Faculty Already a Cross Faculty')
            
            email = str(email)
            cur.execute("select changeCross(%s, %s)", ('dir', str(email)))
            cur.close()
            conn.commit()
            conn.close()
            return render_template('admin.html', path = state.getPath(), status3='Director updated Succesfully')
    return render_template('admin.html', path = state.getPath())

@app.route('/edit', methods = ['GET', 'POST'])
def edit():
    if(state.active_account == None):
        return render_template('login.html')
    if request.method == 'POST':
        if 'Publications' in request.form:
            pub = request.form['infoProf']
            state.addPublication(state.active_account.email, str(pub))
            return redirect(url_for('index'))
        if 'Grants' in request.form:
            pub = request.form['infoProf']
            state.addGrants(state.active_account.email, str(pub))
            return redirect(url_for('index'))
        if 'Awards' in request.form:
            pub = request.form['infoProf']
            state.addAwards(state.active_account.email, str(pub))
            return redirect(url_for('index'))
        if 'Misslaneous' in request.form:
            pub = request.form['infoProf']
            state.addMiss(state.active_account.email, str(pub))
            return redirect(url_for('index'))
        if 'Teaching' in request.form:
            pub = request.form['infoProf']
            state.addTeaching(state.active_account.email, str(pub))
            return redirect(url_for('index'))
        if 'PublicationsD' in request.form:
            pub = request.form['delete']
            try:
                pubI = int(pub)-1
                pubValue = state.find_account_by_email(state.active_account.email).publication[pubI]
                state.deletePublication(state.active_account.email, pubValue)
                print('########', )       
            except:
                return render_template('edit.html', error='Unvalid index')
            return redirect(url_for('index'))
        if 'GrantsD' in request.form:
            pub = request.form['delete']
            try:
                pubI = int(pub)-1
                pubValue = state.find_account_by_email(state.active_account.email).grants[pubI]
                state.deleteGrants(state.active_account.email, pubValue)
                print('########', )       
            except:
                return render_template('edit.html', error='Unvalid index')
            return redirect(url_for('index'))
        if 'AwardsD' in request.form:
            pub = request.form['delete']
            try:
                pubI = int(pub)-1
                pubValue = state.find_account_by_email(state.active_account.email).awards[pubI]
                state.deleteAwards(state.active_account.email, pubValue)
                print('########', )       
            except:
                return render_template('edit.html', error='Unvalid index')
            return redirect(url_for('index'))
        if 'MisslaneousD' in request.form:
            pub = request.form['delete']
            try:
                pubI = int(pub)-1
                pubValue = state.find_account_by_email(state.active_account.email).miss[pubI]
                state.deleteMiss(state.active_account.email, pubValue)
                print('########', )       
            except:
                return render_template('edit.html', error='Unvalid index')
            return redirect(url_for('index'))
        if 'TeachingD' in request.form:
            pub = request.form['delete']
            try:
                pubI = int(pub)-1
                pubValue = state.find_account_by_email(state.active_account.email).teaching[pubI]
                state.deleteTeaching(state.active_account.email, pubValue)
                print('########', )       
            except:
                return render_template('edit.html', error='Unvalid index')
            return redirect(url_for('index'))
        else:
            return render_template('edit.html', error= 'Error in the Request')
            print('&&&&&&&&&&&&&&&&&&&&&&&&&&&')
    return render_template('edit.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        ss = request.form['emailid']
        password = request.form['password'].encode('utf-8')
        if(state.find_account_by_email(ss)):
            hp = state.find_account_by_email(ss).password.encode('utf-8')
            if bcrypt.hashpw(password, hp) == hp:
                state.active_account = state.find_account_by_email(ss)
                if(state.active_account.email == 'admin@admin.com'):
                    return redirect(url_for('admin'))
                return redirect(url_for('index'))
        else:
            msg = 'Invalid Email or Password'
            return render_template('login.html', msg = msg)
    return render_template('login.html')            
        

@app.route('/logout')
def logout():
    state.active_account = None
    return redirect(url_for('login'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if(request.method == 'POST'):
        name = request.form['username']
        email = request.form['emailid']
        password = request.form['password'].encode('utf-8')
        department = request.form['department']
        print('6666% name')
        if not name or not email or not password or not department :
            msg = 'Fill all the info'
            return render_template('register.html', msg = msg)
        
        hashed = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        
        old_account = state.find_account_by_email(email)
        
        # if(' ' in name):
        #     msg = 'Username Cannot contain spaces'
        #     return render_template('register.html', msg = msg)
        

        if old_account:
            msg = 'Account of same email already exists'
            return render_template('register.html', msg = msg)
        
        # try:
        #     conn = psycopg2.connect(database = "project", user = "postgres", password = "123456789", host = "127.0.0.1", port = "5432")
        #     print("Opened database successfully")
        # except:
        #     msg = 'Cannot open database'
        #     return render_template('register.html', msg = msg)

        # try:
        conn = connectgs()
        cur = conn.cursor()
        nLeaves = 40
        cur.execute("insert into faculty(ID, noOfLeaves, department, next_year_leaves) values (%s, %s, %s, %s);  ", (str(email), int(nLeaves), str(department), int(nLeaves)))
        conn.commit()
        conn.close()
        print('################## Done ###############')
        print(str(name), email, department, (hashed).decode('utf-8'))
        state.active_account = state.create_account_by_flask(str(name), email, department, (hashed).decode('utf-8'))
        if(state.active_account.email == 'admin@admin.com'):
            return redirect(url_for('admin'))    
        return redirect(url_for('index'))
        # except:
        #     msg = 'Cannot insert the info in database'
        #     return render_template('register.html', msg = msg)
        
        
    return render_template('register.html')            

@app.route('/show_faculty')
def showFaculty():
    if(state.active_account == None):
        return render_template('login.html')
    conn = connectgs()
    cur = conn.cursor()
    cur.execute("select * from faculty;")
    items = []
    while 1:
        x = cur.fetchone()
        if x is None:
            break
        temp = [t for t in x]
        items.append(temp)
    cur.close()
    conn.close()
    return render_template('show_faculty.html', **locals())


@app.route('/show_crossfaculty')
def showCrossCut():
    if(state.active_account == None):
        return render_template('login.html')
    conn = connectgs()
    cur = conn.cursor()
    cur.execute("select * from crossfaculty;")
    items = []
    while 1:
        x = cur.fetchone()
        if x is None:
            break
        temp = [t for t in x]
        items.append(temp)
    cur.close()
    conn.close()
    return render_template('showCrossCut.html', **locals())


@app.route('/show_hod')
def showHod():
    if(state.active_account == None):
        return render_template('login.html')
    conn = connectgs()
    cur = conn.cursor()
    cur.execute("select * from hod;")
    items = []
    while 1:
        x = cur.fetchone()
        if x is None:
            break
        temp = [t for t in x]
        items.append(temp)
    cur.close()
    conn.close()
    return render_template('show_hod.html', **locals())


@app.route('/show_history_hod')
def show_history_hod():
    if(state.active_account == None):
        return render_template('login.html')
    conn = connectgs()
    cur = conn.cursor()
    cur.execute("select * from historyofhod;")
    items = []
    while 1:
        x = cur.fetchone()
        if x is None:
            break
        temp = [t for t in x]
        items.append(temp)
    cur.close()
    conn.close()
    return render_template('show_historyOfHod.html', **locals())


@app.route('/show_history_cross')
def show_history_cross():
    if(state.active_account == None):
        return render_template('login.html')
    conn = connectgs()
    cur = conn.cursor()
    cur.execute("select * from historyofcrosscut;")
    items = []
    while 1:
        x = cur.fetchone()
        if x is None:
            break
        temp = [t for t in x]
        items.append(temp)
    cur.close()
    conn.close()
    return render_template('showHistoryOfCrossCut.html', **locals())


@app.route('/show_approved_leaves',methods=['GET','POST'])
def show_approved_leaves():
    fid = []
    fid.append(request.args.get('type'))
    fid.append(request.args.get('type2'))
    con = connectgs()
    cur = con.cursor()
    print(fid)
    cur.execute("select distinct leaveid,commenterid from comments where commenterid = '{}' and commenterpos = '{}'".format(fid[1],fid[0]))
    rows = cur.fetchall()
    print(rows)
    rav = []
    for r in rows:
        l = r[0]
        print(l)
        cur.execute("select * from leaves where id = {} and (leavestatus=\'accepted\' or leavestatus=\'rejected\') and position = \'{}\'".format(l,fid[0]))
        # print(cur.fetchall())
        if(cur.rowcount==1):
            fnt = cur.fetchone()
            rav.append([fnt[1],fnt[2],fnt[0]])
            print(fnt, rav)
    return render_template('approved.html',posts=rav)


if __name__ == '__main__':
    global_init()

    if state.find_account_by_email('admin@admin.com') is None:
        password = 'admin@admin.com'
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        state.create_account_by_flask('admin', 'admin@admin.com', 'cse', hashed.decode('utf-8'))
        print('admin up')
    
    
    if not state.isPathSet():
        state.savePath('hod->deanra->director')
    app.run(debug=True)
