import re
from pathlib import Path

#Currently storing only the last files results, either iterate through all file sin the function or append the file
#So a separate function required to iterate through the files and give the name of file to be appended as well
#Find pattern will then have 2 filename args

#list of installation and upgrade scripts
def list_scripts_drop():
    inpPath="../../contrib/babelfishpg_tsql/sql"
    path=Path(inpPath)

    scripts=[]

    for f in path.glob("*.sql"):
        print(f)
        scripts.append(f)

    upgrades=inpPath+'/upgrades'

    pth=Path(upgrades)
   # print(Path.cwd())
   # print(pth)
    for f in pth.glob("*.sql"):
        print(f)
        scripts.append(f)

    for i in scripts:
        find_pattern(i)


def find_pattern(filename):
    with  open(filename, "r") as file, open("temp.out", "a") as expected_file:
        #Pattern from input file
        #print(cfg["pattern"])
        #pat=cfg["pattern"].strip("'")

        #Taking default pattern for now
        pat="^drop "
        #print(pat)
        line = file.readline()

        while line:
            line=line.strip()
            if line.startswith("--"):
                line=file.readline()
                continue
            else:
                match_f=re.search(pat,line,re.I)
                if match_f:
                    print(line)
                    if "(" in line:
                        line=line.split('(')[0]
                        print(line)

                    line=line.rstrip(';')
                    
                    linewords=line.split()
                    stopwords = ['drop','create','view','procedure','function','view','table','cascade','if','exists','owned','by','role','as','or','replace']
                    resultwords  = [word for word in linewords if word.lower() not in stopwords]
                    result = ' '.join(resultwords)
                    print("result : ",result)
                    expected_file.write("Unexpected drop found for object {0} in file {1}\n".format(result,filename))
                    #expected_file.write(result+"\n")
            line=file.readline()




#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##For JDBC tests 

#list of installation and upgrade scripts
def list_scripts():
    inpPath="../../contrib/babelfishpg_tsql/sql"
    path=Path(inpPath)

    scripts=[]

    for f in path.glob("*.sql"):
        print(f)
        scripts.append(f)

    upgrades=inpPath+'/upgrades'

    pth=Path(upgrades)
   # print(Path.cwd())
   # print(pth)
    for f in pth.glob("*.sql"):
        print(f)
        scripts.append(f)

    for i in scripts:
        find_pattern_create(i)


#files for checking function names
def list_files():
    inpPath="../JDBC/input"
    path=Path(inpPath)

    files=[]

    for f in path.rglob("*.*"):
        #print(f)
        files.append(f)
    print(len(files))
    return files




def find_pattern_create(filename):
    with  open(filename, "r") as file, open("temp_create.out", "a") as expected_file:

        #Pattern from input file
        #print(cfg["pattern"])
        #pat=cfg["pattern"].strip("'")

        #Taking default pattern for now
        pat="^create [\w\s]*(view|procedure)"
        # pat="^create "
        #print(pat)
        line = file.readline()

        while line:
            line=line.strip()
            if line.startswith("--"):
                line=file.readline()
                continue
            else:
                match_f=re.search(pat,line,re.I)
                if match_f:
                    # print(line)
                    if "(" in line:
                        line=line.split('(')[0]
                    # if " as " in line.lower():
                    #     line=line.lower().split(' as ')[0]
                    # if " ON " in line:
                    #     line=line.split(' ON ')[0]
                        # print(line)

                    line=line.rstrip(';')
                    
                    linewords=line.split()
                    stopwords = ['drop','create','view','procedure','function','view','table','domain',
                                'index','schema','temporary','aggregate','cascade','if','exists','owned',
                                'by','role','as','or','replace','collation','not','select']
                    resultwords  = [word for word in linewords if word.lower() not in stopwords]
                    result = ' '.join(resultwords)
                    print("result : ",result)

                    flag=False
                    for i in files:
                        with open(i, "r") as testfile:
                            testline=testfile.readline()

                            # result_wo_sys=result.split('.',maxsplit=2)[1]
                            # print(result_wo_sys)
                            # or re.findall(result_wo_sys, testline,re.I)
                            while testline:
                                if testline.strip().startswith("--"):
                                    testline=testfile.readline()
                                    continue

                                elif(re.search(result,testline,re.I)):
                                    flag=True
                                    print("line :   ",testline)
                                    print(result)
                                    print(i,"\n\n")
                                    break
                                testline=testfile.readline()

                    #check_object(result)
                    #expected_file.write("Unexpected drop found for object {0} \n".format(result))
                    if(not flag and "." in result):
                        result_wo_sys=result.split('.',maxsplit=2)[1]
                        print(result_wo_sys)

                        for i in files:
                            with open(i, "r") as testfile:
                                testline=testfile.readline()
                                
                                while testline:
                                    if testline.strip().startswith("--"):
                                        testline=testfile.readline()
                                        continue

                                    elif(re.search(result_wo_sys, testline,re.I)):
                                        flag=True
                                        print("line :   ",testline)
                                        print(result)
                                        print(i,"\n\n")
                                        break
                                    testline=testfile.readline()
                    if not flag:
                        expected_file.write("Could not find tests for {0}\n".format(result))
                    #print(match_f)
            line=file.readline()




#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##For any search


def verify_pattern_def(filename):
    with  open(filename, "r") as file:
        # matches=[]
        # print(cfg["pattern"])
        # pat=cfg["pattern"].strip("'")

#        pat="^create [\w\s]*(function|view)"
        pat="^create ((?!function|view).)*$"
        print(pat)
        line = file.readline()

        while line:
            line=line.strip()
            match_f=re.findall(pat,line,re.I)
            if match_f:
                print(line)
                #print(match_f)
            line=file.readline()
    #print(matches)

# find_pattern_create("demo.txt")

files=list_files()
# find_pattern_create("../../contrib/babelfishpg_tsql/sql/upgrades/babelfishpg_tsql--2.0.0--2.1.0.sql")
# list_scripts()
list_scripts_drop()