from app import app
from flask import Flask, render_template, request, redirect, flash, session
from flaskext.mysql import MySQL
import csv
from flask_wtf import Form
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import validators, ValidationError
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

timetable = Flask(__name__)
app.config.update(dict(
    SECRET_KEY="secretkey",
    WTF_CSRF_SECRET_KEY="secretkey"
))
timetable.secret_key = 'secretey'
mysql = MySQL()
# MySQL configurations
timetable.config['MYSQL_DATABASE_USER'] = 'root'
timetable.config['MYSQL_DATABASE_PASSWORD'] = 'alohomora'
timetable.config['MYSQL_DATABASE_DB'] = 'timetable'
timetable.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(timetable)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')
	
# FACULTY ENTITY
	
@app.route('/faculty_home')
def faculty_home():
	return render_template('faculty_home.html')
	
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
	
@app.route('/load_timeslot')
def load_timeslot():
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


class OddEvenForm(Form):
	oddeve = RadioField('Select semester category: ',choices=[(1,'Odd'),(2,'Even')])
	submit = SubmitField("Next")

oe=-1

@app.route('/start', methods = ['GET', 'POST'])
def start():
	global oe
	form1 = OddEvenForm()
	if request.method == 'POST':
   		oe = request.form['oddeve']
   		return redirect('/Central_Init')
	return render_template('start.html',form=form1,code=302)

ns=-1
semester=-1

@app.route('/Central_Init')
def Central_Init():
	if oe=='1':
		session['semesters']=['3','5','7']
	elif oe=='2':
		session['semesters']=['4','6','8']
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
	semester=session.get('currentsem')
	con=mysql.connect()
	cursor=con.cursor()
	sections=[]
	zeroes=[]
	ss='A'
	for i in range(ns):
		sections.append(ss)
		ss=chr(ord(ss)+1)
		zeroes.append(0)
	for i in range(ns):
		cursor.callproc('create_Class',(semester,sections[i]))
	con.commit()
	session['currentsection']='A'
	session['whatsdone']=zeroes
	return redirect('/subject')
	
subjects=[]
labs=[]

class subForm(Form):
	global subjects
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

@app.route('/subject',methods=['GET','POST'])
def subject():
	form = subForm()
	global subjects
	global labs
	if request.method == 'POST':
		subjects.extend([request.form['subt1'],request.form['subt2'],request.form['subt3'],request.form['subt4'],request.form['subt5']])
		labs.extend([request.form['subl1'],request.form['subl2'],request.form['subl3']])
		return redirect('sectioncentral')
	return render_template('sub.html',form=form)

@app.route('/sectioncentral')
def sectioncentral():
	section=session.get('currentsection')
	zeroes=session.get('whatsdone')
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
	global subjects
	global labs
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
	global subjects
	global labs
	global semester
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
			row.append(data[0][0])
			cursor.callproc('create_Teachessection',(row[0],row[1],row[2],row[4]))
		if labteachers3[i]!="":
			getfac3="select initials from faculty where name like '%"+labteachers3[i]+"'"
			cursor.execute(getfac3)
			data=cursor.fetchall()
			row.append(data[0][0])
			cursor.callproc('create_Teachessection',(row[0],row[1],row[2],row[5]))
		if labteachers4[i]!="":
			getfac4="select initials from faculty where name like '%"+labteachers4[i]+"'"
			cursor.execute(getfac4)
			data=cursor.fetchall()
			row.append(data[0][0])
			cursor.callproc('create_Teachessection',(row[0],row[1],row[2],row[6]))
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
	global labs
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
	global subjects
	global labs
	global semester
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
