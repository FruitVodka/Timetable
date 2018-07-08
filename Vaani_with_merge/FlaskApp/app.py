#from app import app
from flask import Flask, render_template, request, redirect, flash, session
from flaskext.mysql import MySQL
import csv
from flask_wtf import Form
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import validators, ValidationError
#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import create_engine



mysql=MySQL()
app = Flask(__name__)
app.secret_key = "super secret key"

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'time2'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
app.url_map.strict_slashes = False

@app.route('/')
def hi():
	return render_template('index.html')
@app.route('/index')
def index():
	return render_template('index.html')
	
@app.route('/faculty_home')
def faculty_home():
	conn=mysql.connect()
	cursor=conn.cursor()
	cursor.execute("select name from faculty;");    
	x=cursor.fetchall()
	return render_template('faculty_home.html', x=x)


@app.route('/load_faculty')
def load_faculty():
	with open('csv/faculty.csv','r') as csvf:
		rd=csv.reader(csvf)
		rows=[]
		for row in rd:
			rows.append(row)
		v=1
	con=mysql.connect()
	cursor=con.cursor()
	for i in range(len(rows)):
		for j in range(len(rows[i])):
			if rows[i][j]=='' or rows[i][j]==' ' or rows[i][j]=='\t':
				rows[i][j]='NULL';
	count=0
	for i in range(1,len(rows)):		
		cursor.callproc('create_Faculty',(rows[i][0],rows[i][1],rows[i][2],rows[i][3],rows[i][4]))
		data=cursor.fetchall()
		if len(data)==0:
			count+=1
		else:
			ct=str(count+1)
			print('something went wrong while writing record #'+ct+' from faculty.csv to database')
			if len(data[0][0])<=30:
				print('The faculty '+data[0][0]+' has already been inserted. You can modify their details instead.')
				print('If you are sure this is a new faculty, give different initials and try again.' )
	if count==(len(rows)-1):
		print('faculty.csv successfully read and database updated with no errors')
	con.commit()
	return render_template('faculty_home.html',v=v)

@app.route('/faculty_table')
def faculty_table():
	con=mysql.connect()
	cursor=con.cursor()
	view='select* from faculty order by name'
	cursor.execute(view)
	data=cursor.fetchall()
	ord=[]
	for row in data:
		if row[2]=='Chairperson':
			ord.append(1)
		elif row[2]=='Professor':
			ord.append(2)
		elif row[2]=='Associate Professor':
			ord.append(3)
		elif row[2]=='Assistant Professor':
			ord.append(4)
		elif row[2]=='Visiting Faculty':
			ord.append(5)
		else:
			ord.append(6)
	data2=[x for _,x in sorted(zip(ord,data))]
	return render_template('faculty_table.html',data2=data2)
	
@app.route('/delete_one_faculty/<initials>')
def delete_one_faculty(initials):
	con=mysql.connect()
	cursor=con.cursor()
	print(initials)
	delt='delete from faculty where initials="'+initials+'";'
	print(delt)
	cursor.execute(delt)
	data=cursor.fetchall()
	print(data)
	con.commit()
	return redirect("/faculty_table")
	
@app.route('/edit_faculty')
def edit_faculty():
	initials=request.args['initials']
	name=request.args['name']
	designation=request.args['designation']
	phone=request.args['phone']
	email=request.args['email']
	oi=request.args['oldinitials']
	errors=[]
	con=mysql.connect()
	cursor=con.cursor()
	if name:
		modif='update faculty set name="%s" where initials="%s"'%(name,oi)
		cursor.execute(modif)
		data=cursor.fetchall()
		errors.append(data)
	if designation:
		modif='update faculty set designation="%s" where initials="%s"'%(designation,oi)
		print(modif)
		cursor.execute(modif)
		data=cursor.fetchall()
		errors.append(data)
	if phone:
		modif='update faculty set phone="%s" where initials="%s"'%(phone,oi)
		cursor.execute(modif)
		data=cursor.fetchall()
		errors.append(data)
	if email:
		modif='update faculty set email="%s" where initials="%s"'%(email,oi)
		cursor.execute(modif)
		data=cursor.fetchall()
		errors.append(data)
	if initials:
		modif='update faculty set initials="%s" where initials="%s"'%(initials,oi)
		cursor.execute(modif)
		data=cursor.fetchall()
		errors.append(data)
	print(errors)
	for error in errors:
		if error:
			return "Error. Try again"
	con.commit()
	return redirect("/faculty_table")

@app.route('/add_one_faculty_form')
def add_one_faculty_form():
	return render_template("add_one_faculty_form.html")

@app.route('/delete_all_faculty')
def delete_all_faculty():
	con=mysql.connect()
	cursor=con.cursor()
	delall='delete from faculty'
	cursor.execute(delall)
	data=cursor.fetchall()
	print(data)
	v2=1
	con.commit()
	return render_template("faculty_home.html",v2=v2)
	
@app.route('/add_one_faculty')
def add_one_faculty():
	con=mysql.connect()
	cursor=con.cursor()
	initials=request.args['initials']
	name=request.args['name']
	designation=request.args['designation']
	phone=request.args['phone']
	email=request.args['email']
	cursor.callproc('create_Faculty',(initials,name,designation,phone,email))
	data=cursor.fetchall()
	print(data)
	con.commit()
	return redirect('/faculty_home')
	
# TIMESLOT ENTITY
	
@app.route('/timeslot_home')
def timeslot_home():
	return render_template('timeslot_home.html')
	
@app.route('/load_timeslots')
def load_timeslots():
	with open('csv/timeslot.csv','r') as csvf:
		rd=csv.reader(csvf)
		rows=[]
		for row in rd:
			rows.append(row)
		v=1
	con=mysql.connect()
	cursor=con.cursor()
	for i in range(len(rows)):
		for j in range(len(rows[i])):
			if rows[i][j]=='' or rows[i][j]==' ' or rows[i][j]=='\t':
				rows[i][j]='NULL';
	count=0
	for i in range(0,len(rows)):		
		cursor.callproc('create_Timeslot',(rows[i][0],rows[i][1]))
		data=cursor.fetchall()
		if len(data)==0:
			count+=1
	if count==(len(rows)-1):
		print('timeslot.csv successfully read and database updated with no errors')
	else:
		print('failed to read timeslot.csv completely into the database')
	con.commit()
	return render_template('timeslot_home.html',v=v)
	
@app.route('/delete_timeslots')
def delete_timeslots():
	con=mysql.connect()
	cursor=con.cursor()
	delall='delete from timeslot'
	cursor.execute(delall)
	data=cursor.fetchall()
	print(data)
	v2=1
	con.commit()
	return render_template("timeslot_home.html",v2=v2)
	
# SUBJECT AND ELECTIVE ENTITIES
	
@app.route('/subject_home')
def subject_home():
	return render_template('subject_home.html')
	
@app.route('/load_subject')
def load_subject():
	with open('csv/subject.csv','r') as csvf:
		rd=csv.reader(csvf)
		rows=[]
		for row in rd:
			rows.append(row)
		v=1
	con=mysql.connect()
	cursor=con.cursor()
	rows2=[]
	for i in range(len(rows)):
		if not (rows[i][0]=='' and rows[i][1]=='' and rows[i][2]==''):
			rows2.append(rows[i])
	for i in range(len(rows2)):
		for j in range(len(rows2[i])):
			if rows2[i][j]=='' or rows2[i][j]==' ' or rows2[i][j]=='\t':
				rows2[i][j]='NULL';
	print(rows2)
	count=0
	for i in range(1,len(rows2)):		
		cursor.callproc('create_Subject',(rows2[i][0],rows2[i][1],rows2[i][2]))
		data=cursor.fetchall()
		print(data)
		if len(data)==0:
			count+=1
		else:
			print('something went wrong while writing a record from subject.csv to database')
	if count==(len(rows)-1):
		print('subject.csv successfully read and database updated with no errors')
	con.commit()
	return render_template('subject_home.html',v=v)
	
@app.route('/load_elective')
def load_elective():
	with open('csv/elective.csv','r') as csvf:
		rd=csv.reader(csvf)
		rows=[]
		for row in rd:
			rows.append(row)
		v=1
	con=mysql.connect()
	cursor=con.cursor()
	rows2=[]
	for i in range(len(rows)):
		if not (rows[i][0]=='' and rows[i][1]=='' and rows[i][2]==''):
			rows2.append(rows[i])
	for i in range(len(rows2)):
		for j in range(len(rows2[i])):
			if rows2[i][j]=='' or rows2[i][j]==' ' or rows2[i][j]=='\t':
				rows2[i][j]='NULL';
	print(rows2)
	count=0
	for i in range(1,len(rows2)):		
		cursor.callproc('create_Elective',(rows2[i][0],rows2[i][1],rows2[i][2]))
		data=cursor.fetchall()
		print(data)
		if len(data)==0:
			count+=1
		else:
			print('something went wrong while writing a record from elective.csv to database')
	if count==(len(rows)-1):
		print('elective.csv successfully read and database updated with no errors')
	con.commit()
	v3=1
	return render_template('subject_home.html',v3=v3)

@app.route('/delete_subjects')
def delete_subjects():
	con=mysql.connect()
	cursor=con.cursor()
	delalls='delete from subject'
	delalle='delete from elective'
	cursor.execute(delalls)
	data=cursor.fetchall()
	print(data)
	cursor.execute(delalle)
	data=cursor.fetchall()
	print(data)
	v2=1
	con.commit()
	return render_template("subject_home.html",v2=v2)
	
@app.route('/subject_table')
def subject_table():
	con=mysql.connect()
	cursor=con.cursor()
	views='select* from subject order by title'
	cursor.execute(views)
	datas=cursor.fetchall()
	viewe='select* from elective order by pool, title'
	cursor.execute(viewe)
	datae=cursor.fetchall()
	return render_template('subject_table.html',datas=datas,datae=datae)
	
# ROOM ENTITY
	
@app.route('/room_home')
def room_home():
	return render_template('room_home.html')
	
@app.route('/load_rooms')
def load_rooms():
	with open('csv/room.csv','r') as csvf:
		rd=csv.reader(csvf)
		rows=[]
		for row in rd:
			rows.append(row)
		v=1
	con=mysql.connect()
	cursor=con.cursor()
	for i in range(len(rows)):
		for j in range(len(rows[i])):
			if rows[i][j]=='' or rows[i][j]==' ' or rows[i][j]=='\t':
				rows[i][j]='NULL';
	count=0
	for i in range(0,len(rows)):		
		cursor.callproc('create_Room',(rows[i][0],rows[i][1]))
		data=cursor.fetchall()
		if len(data)==0:
			count+=1
	if count==(len(rows)-1):
		print('room.csv successfully read and database updated with no errors')
	else:
		print('failed to read room.csv completely into the database')
	con.commit()
	return render_template('room_home.html',v=v)
	
@app.route('/delete_rooms')
def delete_rooms():
	con=mysql.connect()
	cursor=con.cursor()
	delall='delete from room'
	cursor.execute(delall)
	data=cursor.fetchall()
	print(data)
	v2=1
	con.commit()
	return render_template("room_home.html",v2=v2)


	
	
	
	
#FROM START
	
class OddEvenForm(Form):
	oddeve = RadioField('Select semester category: ',choices=[(1,'Odd'),(2,'Even')])
	submit = SubmitField("Next")

@app.route('/start', methods = ['GET', 'POST'])
def start():
	oe=-1
	form1 = OddEvenForm()
	if request.method == 'POST':
		oe = request.form['oddeve']
		session['oe']=oe
		return redirect('/Central_Init')
	return render_template('start.html',form=form1,code=302)

@app.route('/Central_Init')
def Central_Init():
	oe=session.get('oe')
	if oe=='1':
		session['semesters']=['3','5','7']
		session['group']=1
	elif oe=='2':
		session['semesters']=['4','6','8']
		session['group']=3
	session['currentsem']=session.get('semesters')[0]
	return redirect('/Central')

@app.route('/Central')
def Central():
	currentsem=session.get('currentsem')
	semesters=session.get('semesters')
	if currentsem==semesters[0]:
		nextsem=semesters[1]
	elif currentsem==semesters[1]:
		nextsem=semesters[2]
	elif currentsem==semesters[2]:
		nextsem="NULL"
	elif currentsem=="NULL":
		return "All wrapped up! Everything's sitting in the database!"
	session['currentsem']=nextsem
	return render_template('picksections.html',currentsem=currentsem)

@app.route('/pickedsections', methods=['GET','POST'])
def pickedsections():
	ns=request.form.getlist('number_of_sections')[0]
	#for current semester
	nextsem=session.get('currentsem')
	semesters=session.get('semesters')
	if(nextsem!='NULL'):
		semester=str(eval(nextsem)-2)
	else:
		semester=semesters[2]
	con=mysql.connect()
	cursor=con.cursor()
	sections=[]
	zeroes=[]
	ss='A'
	for i in range(eval(ns)):
		sections.append(ss)
		ss=chr(ord(ss)+1)
		zeroes.append(0)
	for i in range(eval(ns)):
		cursor.callproc('create_Class',(semester,sections[i]))
	con.commit()
	session['currentsection']='A'
	session['whatsdone']=zeroes
	return redirect('/check_electives')

@app.route('/check_electives',	methods=['GET','POST'])
def check_electives():
	#for current semester
	nextsem=session.get('currentsem')
	semesters=session.get('semesters')
	if(nextsem!='NULL'):
		semester=str(eval(nextsem)-2)
	else:
		semester=semesters[2]
	if semester=='3' or semester=='4':
		return redirect('/subject')
	else:
		return redirect('/freeze')

@app.route('/freeze', methods=['GET', 'POST'])
def freeze():
	gr=session.get('group')
	return render_template('freeze_elective.html', gr=gr)

@app.route('/after_freeze', methods=['GET', 'POST'])
def after_freeze():
	group=session.get('group')
	mon=request.form.getlist("Monday")
	tue=request.form.getlist("Tuesday")
	wed=request.form.getlist("Wednesday")
	thu=request.form.getlist("Thursday")
	fri=request.form.getlist("Friday")
	times=[]
	day=[]
	if len(mon)>0:
		day.append('Monday')
		for i in range(0, len(mon)):
			if mon[i]!='':
				if mon[i][1]=='1':
					times.append('8:15-9:15')
					times.append('9:15-10:15')
				elif mon[i][1]=='5':
					times.append('1:30-2:30')
					times.append('2:30-3:30')
	if len(tue)>0:
		day.append('Tuesday')
		for i in range(0, len(tue)):
			if tue[i]!='':
				if tue[i][1]=='1':
					times.append('8:15-9:15')
					times.append('9:15-10:15')
				elif tue[i][1]=='5':
					times.append('1:30-2:30')
					times.append('2:30-3:30')
	if len(wed)>0:
		day.append('Wednesday')
		for i in range(0, len(wed)):
			if wed[i]!='':
				if wed[i][1]=='1':
					times.append('8:15-9:15')
					times.append('9:15-10:15')
				elif wed[i][1]=='5':
					times.append('1:30-2:30')
					times.append('2:30-3:30')
	if len(thu)>0:
		day.append('Thursday')		
		for i in range(0, len(thu)):
			if thu[i]!='':
				day.append('Thursday')
				if thu[i][1]=='1':
					times.append('8:15-9:15')
					times.append('9:15-10:15')
				elif thu[i][1]=='5':
					times.append('1:30-2:30')
					times.append('2:30-3:30')
	if len(fri)>0:
		day.append('Friday')
		for i in range(0, len(fri)):
			if fri[i]!='':
				day.append('Friday')
				if fri[i][1]=='1':
					times.append('8:15-9:15')
					times.append('9:15-10:15')
				elif fri[i][1]=='5':
					times.append('1:30-2:30')
					times.append('2:30-3:30')
	#conn=mysql.connect()
	#cursor=conn.cursor()
	#cursor.execute("insert into elective_freeze values ("+group+",'"+times[0]+"','"+times[1]+"','"+day[0]+"');")
	#cursor.execute("insert into elective_freeze values ("+group+",'"+times[2]+"','"+times[3]+"','"+day[1]+"');")
	#conn.commit()
	session['times']=times
	session['day']=day
	conn=mysql.connect()
	cursor=conn.cursor()
	cursor.execute("select * from elective where pool="+str(group)+";");    
	x=cursor.fetchall()
	conn.close()
	w=[]
	for i in range(0, len(x)):
		w.append(0)
	w[0]=1
	session['electives']=w
	return redirect("/before_elective")	
	
@app.route('/before_elective', methods=['GET', 'POST'])
def before_elective():
	conn=mysql.connect()
	cursor=conn.cursor()
	gr=session.get('group')
	cursor.execute("select * from elective where pool="+str(gr)+";");    
	x=cursor.fetchall()
	conn.close()
	conn=mysql.connect()
	cursor=conn.cursor()
	cursor.execute("select name from faculty");    
	y=cursor.fetchall()
	conn.close()
	conn=mysql.connect()
	cursor=conn.cursor()
	cursor.execute("select roomno from room;");    
	z=cursor.fetchall()
	l=[]
	open ('electives.csv', 'w')
	for i in range(0, len(x)):
		l.append(0)
	print(l)
	l[0]=1
	session['elective_g1']=l
	conn.close()
	session['ele_code']=x[0][0]
	session['ele_name']=x[0][1]
	session['gr']=1
	return render_template("elective.html", x=x[0], y=y, z=z)


@app.route('/elective_rep', methods=['GET', 'POST'])
def elective_rep():
	w=session.get('elective_g1', None)
	v=session.get('group')
	print(v)
	flag=0
	count=0
	for i in range(0, len(w)):
		if w[i]==1:
			count+=1
		elif w[i]==0:
			w[i]=1
			flag=1 
			break;
	print(count)
	print(w)
	session['elective_g1']=w
	
	conn=mysql.connect()
	cursor=conn.cursor()
	cursor.execute("select name from faculty;");    
	y=cursor.fetchall()
	conn.close()
	
	conn=mysql.connect()
	cursor=conn.cursor()
	cursor.execute("select roomno from room;");    
	z=cursor.fetchall()
	conn.close()
	
	conn=mysql.connect()
	cursor=conn.cursor()
	cursor.execute("select * from elective where pool="+str(v)+";");    
	x=cursor.fetchall()
	conn.close()
	print(x)
	
	elective_name=session.get('ele_name')
	elective_code=session.get('ele_code')
	Teacher=request.form.getlist("Teacher")
	Room=request.form.getlist("Room")
	CoTeacher=request.form.getlist("CoTeacher")
	
	times=session.get('times')
	day=session.get('day')
	conn=mysql.connect()
	cursor=conn.cursor()
	for i in range(0, len(Teacher)):
		cursor.execute("insert into teaches_elective values ('"+elective_code+"','"+elective_name+"','"+Teacher[i]+"','"+CoTeacher[i]+"','"+Room[i]+"','"+times[0]+"','"+times[1]+"','"+day[0]+"',"+str(v)+");")
		cursor.execute("insert into teaches_elective values ('"+elective_code+"','"+elective_name+"','"+Teacher[i]+"','"+CoTeacher[i]+"','"+Room[i]+"','"+times[2]+"','"+times[3]+"','"+day[1]+"',"+str(v)+");")
	conn.commit()
	conn.close()
	
	if flag==0:
		if v==1:
			session['group']=2	
			return render_template("freeze_elective.html", gr=2)
		elif v==2:
			session['group']=5	
			return redirect("/subject")
		elif v==3:
			session['group']=4
			return render_template("freeze_elective.html", gr=4)
		elif v==4:
			session['group']=7
			return redirect("/subject")
		elif v==5:
			session['group']=6
			return render_template("freeze_elective.html", gr=6)
		elif v==6:
			session['group']=0
			return redirect("/subject")
		elif v==7:
			session['group']=0
			return redirect("/subject")
	session['ele_name'] = x[count][1]
	session['ele_code']=x[count][0]
	return render_template("elective.html", x=x[count], y=y, z=z)

class subForm(Form):
	con=mysql.connect()
	cursor=con.cursor()
	view='select code, title from subject order by title'
	cursor.execute(view)
	data=cursor.fetchall()
	arr=[list(item) for item in data]
	for i in range(0,len(data)):
		arr[i][0]=arr[i][1]
	subt1 = SelectField('Subject 1',choices=arr)
	subt2 = SelectField('Subject 2',choices=arr)
	subt3 = SelectField('Subject 3',choices=arr)
	subt4 = SelectField('Subject 4',choices=arr)
	subt5 = SelectField('Subject 5',choices=arr)
	subl1 = SelectField('Lab 1',choices=arr)
	subl2 = SelectField('Lab 2',choices=arr)
	subl3 = SelectField('Lab 3',choices=arr)
	submit = SubmitField("Send")
	
class sub2Form(Form):
	con=mysql.connect()
	cursor=con.cursor()
	view='select code, title from subject order by title'
	cursor.execute(view)
	data=cursor.fetchall()
	arr=[list(item) for item in data]
	for i in range(0,len(data)):
		arr[i][0]=arr[i][1]
	subt1 = SelectField('Subject 1',choices=arr)
	subt2 = SelectField('Subject 2',choices=arr)
	subt3 = SelectField('Subject 3',choices=arr)
	subl1 = SelectField('Lab 1',choices=arr)
	subl2 = SelectField('Lab 2',choices=arr)
	subl3 = SelectField('Lab 3',choices=arr)	
	submit = SubmitField("Send")

@app.route('/subject',methods=['GET','POST'])
def subject():
	subjects=[]
	labs=[]
	nextsem=session.get('currentsem')
	semesters=session.get('semesters')
	if nextsem=='5' or nextsem=='6':
		form=subForm()
	elif nextsem=='7' or nextsem=='8' or (nextsem=='NULL' and semesters[2]=='8') or (nextsem=='NULL' and semesters[2]=='7'):
		form=sub2Form()
	if nextsem=='NULL' and semesters[2]=='8':
		return "must go to electives"
	if request.method == 'POST':
		#working with semester 3 or 4
		if nextsem=='5' or nextsem=='6':
			subjects.extend([request.form['subt1'],request.form['subt2'],request.form['subt3'],request.form['subt4'],request.form['subt5']])
			labs.extend([request.form['subl1'],request.form['subl2'],request.form['subl3']])
		#working with semester 5, 6 or 7
		elif nextsem=='7' or nextsem=='8' or (nextsem=='NULL' and semesters[2]=='7'):
			subjects.extend([request.form['subt1'],request.form['subt2'],request.form['subt3']])
			labs.extend([request.form['subl1'],request.form['subl2'],request.form['subl3']])
		session['subjects']=subjects
		session['labs']=labs
		return redirect('sectioncentral')
	return render_template('sub.html',form=form)

@app.route('/sectioncentral')
def sectioncentral():
	section=session.get('currentsection')
	zeroes=session.get('whatsdone')
	#for current semester
	nextsem=session.get('currentsem')
	semesters=session.get('semesters')
	if(nextsem!='NULL'):
		semester=str(eval(nextsem)-2)
	else:
		semester=semesters[2]
	flag=0
	for i in range(len(zeroes)):
		if zeroes[i]==0:
			zeroes[i]=1
			flag=1
			break
	if(flag==0):
		return redirect('/Central')
	session['whatsdone']=zeroes
	nextsection=chr(ord(section)+1)
	session['currentsection']=nextsection
	con=mysql.connect()
	cursor=con.cursor()
	fac="select name from faculty"
	cursor.execute(fac)
	data=cursor.fetchall()
	fac=data
	subjects=session.get('subjects')
	labs=session.get('labs')
	print(subjects, labs)
	return render_template('pickteachers.html',semester=semester,section=section,subjects=subjects,fac=fac,labs=labs)
	
@app.route('/pickedteachers', methods=['GET', 'POST'])
def pickedteachers():
	theoryteachers= request.form.getlist('theoryteachers')
	labteachers1=request.form.getlist('labteachers1')
	labteachers2=request.form.getlist('labteachers2')
	labteachers3=request.form.getlist('labteachers3')
	labteachers4=request.form.getlist('labteachers4')
	print(theoryteachers)
	print("")
	print(labteachers1, labteachers2, labteachers3, labteachers4)
	row=[]
	subjects=session.get('subjects')
	labs=session.get('labs')
	#for current semester
	nextsem=session.get('currentsem')
	semesters=session.get('semesters')
	if(nextsem!='NULL'):
		semester=str(eval(nextsem)-2)
	else:
		semester=semesters[2]
	con=mysql.connect()
	cursor=con.cursor()
	for i in range(len(subjects)):
		next=session.get('currentsection')
		cur=chr(ord(next)-1)
		row.append(str(semester))
		row.append(cur)
		getsub="select code from subject where title='%s'"%subjects[i]
		getfac="select initials from faculty where name like '%"+theoryteachers[i]+"'"
		cursor.execute(getsub)
		data=cursor.fetchall()
		row.append(data[0][0])
		cursor.execute(getfac)
		data=cursor.fetchall()
		row.append(data[0][0])
		cursor.callproc('create_Teachessection',(row[0],row[1],row[2],row[3]))
		data=cursor.fetchall()
		print(data)
		row=[]
	for i in range(len(labs)):
		next=session.get('currentsection')
		cur=chr(ord(next)-1)
		row.append(str(semester))
		row.append(cur)
		getsub="select code from subject where title='%s'"%labs[i]
		cursor.execute(getsub)
		data=cursor.fetchall()
		row.append(data[0][0])
		getfac1="select initials from faculty where name like '%"+labteachers1[i]+"'"
		cursor.execute(getfac1)
		data=cursor.fetchall()
		row.append(data[0][0])
		cursor.callproc('create_Teachessection',(row[0],row[1],row[2],row[3]))
		if labteachers2[i]!="":
			getfac2="select initials from faculty where name like '%"+labteachers2[i]+"'"
			cursor.execute(getfac2)
			data=cursor.fetchall()
			row[3]=data[0][0]
			cursor.callproc('create_Teachessection',(row[0],row[1],row[2],row[3]))
		if labteachers3[i]!="":
			getfac3="select initials from faculty where name like '%"+labteachers3[i]+"'"
			cursor.execute(getfac3)
			data=cursor.fetchall()
			row[3]=data[0][0]
			cursor.callproc('create_Teachessection',(row[0],row[1],row[2],row[3]))
		if labteachers4[i]!="":
			getfac4="select initials from faculty where name like '%"+labteachers4[i]+"'"
			cursor.execute(getfac4)
			data=cursor.fetchall()
			row[3]=data[0][0]
			cursor.callproc('create_Teachessection',(row[0],row[1],row[2],row[3]))
		row=[]
	con.commit()
	return redirect('/pickrooms')

@app.route('/pickrooms')
def pickrooms():
	section=session.get('currentsection')
	section=chr(ord(section)-1)
	zeroes=session.get('whatsdone')
	con=mysql.connect()
	cursor=con.cursor()
	cr="select roomno from room"
	cursor.execute(cr)
	data=cursor.fetchall()
	classrooms=data
	#for current semester
	nextsem=session.get('currentsem')
	semesters=session.get('semesters')
	if(nextsem!='NULL'):
		semester=str(eval(nextsem)-2)
	else:
		semester=semesters[2]
	labs=session.get('labs')
	return render_template('pickrooms.html',semester=semester,section=section,labs=labs,classrooms=classrooms)

@app.route('/pickedrooms', methods=['GET', 'POST'])
def pickedrooms():
	theoryroom= request.form.getlist('theoryroom')
	labroom1=request.form.getlist('labroom1')
	labroom2=request.form.getlist('labroom2')
	print(theoryroom)
	print("")
	print(labroom1, labroom2)
	row=[]
	subjects=session.get('subjects')
	labs=session.get('labs')
	#for current semester
	nextsem=session.get('currentsem')
	semesters=session.get('semesters')
	if(nextsem!='NULL'):
		semester=str(eval(nextsem)-2)
	else:
		semester=semesters[2]
	con=mysql.connect()
	cursor=con.cursor()
	for i in range(len(subjects)):
		next=session.get('currentsection')
		cur=chr(ord(next)-1)
		row.append(str(semester))
		row.append(cur)
		getsub="select code from subject where title='%s'"%subjects[i]
		cursor.execute(getsub)
		data=cursor.fetchall()
		row.append(data[0][0])
		row.append(theoryroom)
		cursor.callproc('create_Roomssection',(row[0],row[1],row[2],row[3]))
		data=cursor.fetchall()
		print(data)
		row=[]
	for i in range(len(labs)):
		next=session.get('currentsection')
		cur=chr(ord(next)-1)
		row.append(str(semester))
		row.append(cur)
		getsub="select code from subject where title='%s'"%labs[i]
		cursor.execute(getsub)
		data=cursor.fetchall()
		row.append(data[0][0])
		row.append(labroom1[i])
		cursor.callproc('create_Roomssection',(row[0],row[1],row[2],row[3]))
		if labroom2[i]!="":
			row.append(labroom2[i])
			cursor.callproc('create_Roomssection',(row[0],row[1],row[2],row[4]))
		row=[]
	con.commit()
	return redirect('/sectioncentral')

if __name__ == '__main__':
    app.run()