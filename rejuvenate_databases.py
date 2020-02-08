import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from getpass import getpass
pss = ""
def connectdb(s1):
	return psycopg2.connect(database=s1, user="postgres", password=pss)

def create_db():
	con = connectdb('postgres')
	con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
	cur = con.cursor()
	try:
		cur.execute('drop database project;')
		con.commit()
	except:
		print('creating and initializing databases')
	cur.execute('create database project')
	cur.close()
	con.close()
	con = connectdb("project")
	con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
	cur = con.cursor()
	cur.execute('''
		create table department(
			id VARCHAR(50) NOT NULL PRIMARY KEY,
			name VARCHAR(50) NOT NULL UNIQUE
			 );
		''')
	cur.execute('''
		insert into department values('cse','Computer Science');
		insert into department values('mec','Mechanical');
		insert into department values('che','Chemical');
		insert into department values('eee','Electrical');
		''')
	cur.execute('''
		create table faculty(
			Id VARCHAR(50) NOT NULL PRIMARY KEY,
			noOfLeaves integer NOT NULL,
			department VARCHAR(50) NOT NULL,
			next_year_leaves integer,
			FOREIGN KEY(department) references department(id)
		);
		''')
	

	cur.execute('''
		create table HOD(
			facultyId VARCHAR(50) NOT NULL,
			DepartName VARCHAR(50) NOT NULL,
			startTime timestamp,
			PRIMARY KEY(facultyId, DepartName),
			FOREIGN KEY(DepartName) references department(id),
			FOREIGN KEY(facultyId) references faculty(Id)
			);
			''')


	cur.execute('''
		create table crossFaculty(
			facultyId VARCHAR(50) NOT NULL,
			position VARCHAR(50) NOT NULL PRIMARY KEY,
			startTime timestamp,
			FOREIGN KEY(facultyId) references faculty(Id)
			);
			''')


	cur.execute('''
		create table leaves(id SERIAL PRIMARY KEY,
					leavestatus VARCHAR(50) NOT NULL,
					facultyid VARCHAR(50) NOT NULL,
					position VARCHAR(50),
					positionid VARCHAR(50) NOT NULL,
					days integer,
					lastupdated timestamp default now(),
					path VARCHAR(50),
					note integer,
					FOREIGN KEY(facultyId) references faculty(Id),
					FOREIGN KEY(positionid) references faculty(Id))
					''')
	cur.execute('''
	create table comments(leaveid INTEGER NOT NULL,
					comment VARCHAR(100) NOT NULL,
					commenterid VARCHAR(50),
					commenterpos VARCHAR(50),
					timeofcomment timestamp default now(),
					FOREIGN KEY(commenterid) references faculty(Id))
					''')
	cur.execute('''
		create table historyOfHod(
			departmentName VARCHAR(50) NOT NULL,
			facultyId VARCHAR(50) NOT NULL,
			startTime timestamp,
			endTime timestamp,
			FOREIGN KEY(departmentName) references department(id),
			FOREIGN KEY(facultyId) references faculty(Id)
		);
	''')

	cur.execute('''
		create table historyOfCrossCut(
        facultyId VARCHAR(50) NOT NULL,
        position VARCHAR(50) NOT NULL,
        startTime timestamp,
        endTime timestamp,
        FOREIGN KEY(facultyId) references faculty(Id),
        FOREIGN KEY(position) references crossFaculty(position)
    );
	''')

	cur.execute('''
		create or replace function changeHod(department VARCHAR(50), faculty VARCHAR(50))
		returns void as $$
		declare
		check_ integer;
		begin
			select count(DepartName) into check_
			from hod
			where DepartName = department;
			if(check_ >= 1) then
				update hod 
					set facultyId = faculty, startTime = now()
					where DepartName = department;
			else
				insert into hod(facultyId, DepartName, startTime) values (faculty, department, now());
			end if;
			return;
		end;
		$$
		language plpgsql;


		create or replace function changedHodTriggerUpdate()
		returns TRIGGER as $$
		declare
		begin
			insert into historyOfHod(departmentName, facultyId, startTime, endTime) values (old.DepartName, old.facultyId, old.startTime, now());
			return new;
		end;
		$$
		language plpgsql;


		-- return old
		create or replace function changedHodTriggerDelete()
		returns TRIGGER as $$
		declare
		begin
			insert into historyOfHod(departmentName, facultyId, startTime, endTime) values (old.DepartName, old.facultyId, old.startTime, now());
			return old;
		end;
		$$
		language plpgsql;


		create TRIGGER HodChangeLog1
		before update
		on HOD
		for each row
		execute procedure changedHodTriggerUpdate();


		
		create TRIGGER HodChangeLog2
		before delete
		on HOD
		for each row
		execute procedure changedHodTriggerDelete();



		-- # DIR
		-- # DEANAA
		-- # DEANRA
		-- # DEANSA
		-- # ADEANFA
		-- # ADEANAA
		-- # ADEANRA
		-- # ADEANSA

		create or replace function changeCross(position_ VARCHAR(50), faculty VARCHAR(50))
		returns void as $$
		declare
		check_ integer;

		begin
			select count(position) into check_
			from crossFaculty
			where position = position_;
			if(check_ >= 1) then
				update crossFaculty 
					set facultyId = faculty, startTime = now()
					where position = position_;
			else
				insert into crossFaculty(facultyId, position, startTime) values (faculty, position_, now());
			end if;
			
			
		end;
		$$
		language plpgsql;



		create or replace function changedCrossTriggerUpdate()
		returns TRIGGER as $$
		declare

		begin
			insert into historyOfCrossCut(facultyId, position, startTime, endTime) values (old.facultyId, old.position, old.startTime, now());
			return new;
		end;
		$$
		language plpgsql;


		create or replace function changedCrossTriggerDelete()
		returns TRIGGER as $$
		declare

		begin
			insert into historyOfCrossCut(facultyId, position, startTime, endTime) values (old.facultyId, old.position, old.startTime, now());
			return old;
		end;
		$$
		language plpgsql;



		create TRIGGER CrossChangeLog1
		before update
		on crossFaculty
		for each row
		execute procedure changedCrossTriggerUpdate();


		create TRIGGER CrossChangeLog2
		before delete
		on crossFaculty
		for each row
		execute procedure changedCrossTriggerDelete();


		''')

	cur.close()
	con.commit()
	con.close()
	



if __name__ == '__main__':
	pss = getpass('databse password: ')
	create_db()
