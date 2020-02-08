import psycopg2
import program


cur = program.getConn().cursor()
cur.execute('''SELECT now();''')
print("Table created successfully", cur.fetchone())
cur.execute('''
    create table department(
        name VARCHAR(50) NOT NULL UNIQUE,
        id VARCHAR(50) NOT NULL PRIMARY KEY
        );
''')


cur.execute('''
    create table faculty(
        Id VARCHAR(50) NOT NULL PRIMARY KEY,
        noOfLeaves integer NOT NULL,
        department VARCHAR(50) NOT NULL,
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
    create table crossFaculty(
        facultyId VARCHAR(50) NOT NULL,
        position VARCHAR(50) NOT NULL PRIMARY KEY,
        startTime timestamp,
        FOREIGN KEY(facultyId) references faculty(Id)
    )
''')

cur.execute('''
    create table historyOfCrossCut(
        facultyId VARCHAR(50) NOT NULL,
        position VARCHAR(50) NOT NULL,
        startTime timestamp,
        endTime timestamp,
        FOREIGN KEY(facultyId) references faculty(Id),
        FOREIGN KEY(position) references crossFaculty(position)
    )
''')


program.getConn().commit()
program.getConn().close()
