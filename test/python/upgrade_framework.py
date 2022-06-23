import re
from pathlib import Path
import subprocess
import sys
from utils.config import config_dict as cfg

#Find pattern will then have 2 filename args

#list of installation and upgrade scripts
def list_scripts_drop():
    inpPath="../../contrib"
    path=Path(inpPath)
    scripts=[]

    for f in path.glob("*/sql/upgrades/*.sql"):
        scripts.append(f)

    # path=path.joinpath("upgrades")
    # for f in path.glob("*.sql"):
    #     # print(f)
    #     scripts.append(f)
    return scripts


def find_pattern_drop():
    path = Path.cwd().joinpath("output", "Script_verif_framework")
    Path.mkdir(path, parents = True, exist_ok = True)
    f_path = path.joinpath("drop-found.out")
    with open(f_path, "w") as expected_file:
        scripts=list_scripts_drop()
        pat=r"^drop "
        #print(pat)

        for filename in scripts:
            with  open(filename, "r") as file:
  
                line = file.readline()

                readflag=True
                while line:
                    line=line.strip()
                    if line.startswith("--") or line.startswith("/*") or line.startswith("#"):
                        line=file.readline()
                        continue
                    elif readflag==True:
                        match_f=re.search(pat,line,re.I)
                        if match_f:
                            print(filename)
                            print(line)
                            if "(" in line:
                                line=line.split('(')[0]
                                print(line)

                            line=line.rstrip(';')
                            if "using" in line.lower():
                                line=line.lower().split('using')[0]

                            linewords=line.split()
                            object_category=['table','view','function','procedure','role','class','operator','cast']
                            category='object'
                            for word in linewords:
                                if word.lower() in object_category:
                                    category=word.lower()
                                    break
                            if category=='class':
                                category='operator class'
                            
                            stopwords = ['drop','create','view','procedure','function','view','table','cascade','if','exists','owned','by','role','as','or','replace','class','operator','cast']
                            resultwords  = [word for word in linewords if word.lower() not in stopwords]
                            obj_name = ' '.join(resultwords)
                            print("result : ",obj_name)
                            expected_file.write("Unexpected drop found for {0} {1} in file {2}\n".format(category,obj_name,filename))
                    if len(re.findall(r"[$]{2}",line,re.I)) == 1:
                        readflag=not readflag
                    line=file.readline()




#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##For JDBC tests 

#list of installation and upgrade scripts
def list_scripts_create():
    inpPath="../../contrib/babelfishpg_tsql/sql"
    path=Path(inpPath)

    scripts=[]

    for f in path.glob("*.sql"):
        print(f)
        scripts.append(f)

    path=path.joinpath("upgrades")
    for f in path.glob("*.sql"):
        # print(f)
        scripts.append(f)

    #Removing helper functions
    scripts.remove(Path(inpPath+"/sys_function_helpers.sql"))
    return scripts


#List of files in JDBC framework
def list_files(inpPath):
    path=Path(inpPath)

    files=[]

    for f in path.rglob("*.*"):
        #print(f)
        files.append(f)
    return files



def find_pattern_create():
    scripts=list_scripts_create()
    object_names=set()
    #pat=r"^create [\w\s]*\b(view)\b"
    pat=r"^create [\w\s]*\b({0})\b".format(cfg["createObjectSearch"].replace(',','|'))
    for filename in scripts:
        with  open(filename, "r") as file:

            print(filename)
            line = file.readline()

            readflag=True
            while line:
                line=line.strip()
                if line.startswith("--") or line.startswith("/*") or line.startswith("#"):
                    line=file.readline()
                    continue
                elif readflag==True:
                    match_f=re.search(pat,line,re.I)
                    if match_f:
                        print(line)
                        if "(" in line:
                            line=line.split('(')[0]+"[(]"
                        
                        # if " as " in line.lower():
                        #     line=line.lower().split(' as ')[0]
                        # if " ON " in line:
                        #     line=line.split(' ON ')[0]
                            # print(line)

                        line=line.rstrip(';')
                        linewords=line.split()
                        object_category=['table','view','function','procedure','role','aggregate','schema','domain','collation','index']
                        category='object'
                        for word in linewords:
                            if word.lower() in object_category:
                                category=word.lower()
                        stopwords = ['drop','create','view','procedure','function','table','domain',
                                    'index','schema','temporary','aggregate','cascade','if','exists','owned',
                                    'by','role','as','or','replace','collation','not','select']
                        resultwords  = [word for word in linewords if word.lower() not in stopwords]
                        obj_name = ' '.join(resultwords)

                        print("word to be searched : ",obj_name.lower())

                        object_names.add((category,obj_name))
                if len(re.findall(r"[$]{2}",line,re.I)) == 1:
                    readflag=not readflag    
                line=file.readline()
    print(object_names)
    return object_names


def find_inp_JDBC():
    files=list_files("../JDBC/input")
    object_name=find_pattern_create()
    path = Path.cwd().joinpath("output", "Script_verif_framework")
    Path.mkdir(path, parents = True, exist_ok = True)
    f_path = path.joinpath("tests-not-found.out")
    with open(f_path, "w") as expected_file:
        for object in object_name:

            #Flag for object name found or not in the JDBC input files
            flag=False
            print(object[1])
            for i in files:
                with open(i, "r") as testfile:
                    testline=testfile.readline()

                    while testline:
                        testline=testline.strip()
                        if testline.startswith("--") or testline.startswith("/*") or testline.startswith("#"):
                            testline=testfile.readline()
                            continue

                        elif(re.search(r"\b"+object[1]+r"\b",testline,re.I)):
                            flag=True
                            print("Found\nline :   ",testline)
                            print("file name : ",i)
                            break
                        testline=testfile.readline()
                    else:
                        continue
                    break

            if(flag==False and "sys." in object[1]):
                result_wo_sys=object[1].split('.',maxsplit=2)[1]

                for i in files:
                    with open(i, "r") as testfile:
                        testline=testfile.readline()
                                
                        while testline:
                            testline=testline.strip()
                            if testline.startswith("--") or testline.startswith("/*") or testline.startswith("#"):
                                testline=testfile.readline()
                                continue

                            elif(re.search(r"\b"+result_wo_sys+r"\b", testline,re.I)):
                                flag=True
                                print("Found\nline :   ",testline)
                                print("file name : ",i)
                                break
                            testline=testfile.readline()
                        else:
                            continue
                        break
            if flag==False:
                expected_file.write("Could not find tests for {0} {1}\n".format(object[0],object[1]))
            #print(match_f)


#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##For any search


def find_patterns():
    files=list_files("../../contrib/babelfishpg_tsql/sql/upgrades")
    path = Path.cwd().joinpath("output", "Script_verif_framework")
    Path.mkdir(path, parents = True, exist_ok = True)
    f_path = path.joinpath("Pattern_match_results.out")
    with open(f_path, "w") as expected_file:
        patterns=cfg["searchPatterns"].split(',')
            # pat="^create [\w\s]*(function|view)"
            # pat="^create ((?!function|view).)*$"
        for pattern in patterns:
            # pattern = r"{0}".format(pattern)
            # pattern="query\d"
            # print(pattern)
            expected_file.write("Pattern : {0} \n".format(pattern))
            for filename in files:
                with  open(filename, "r") as file:
                    # matches=[]
                    # print(cfg["pattern"])
                    # pat=cfg["pattern"].strip("'")

                    line = file.readline()

                    while line:
                        match_f=re.findall(pattern,line,re.I)
                        if match_f:
                            # print(line)
                            expected_file.write("{0} \n".format(line))
                        line=file.readline()

# find_pattern_create("demo.txt")

# def compare_outfiles(outfile, expected_file, logfname, filename, logger):
#     try:
#         diff_file = Path.cwd().joinpath("logs", logfname, filename, filename + ".diff")
#         f_handle = open(diff_file, "wb")

#         if "sql_expected" in expected_file.as_uri():
#             if sys.platform.startswith("win"):
#                 proc = subprocess.run(args = ["fc", expected_file, outfile], stdout = f_handle, stderr = f_handle)
#             else:
#                 proc = subprocess.run(args = ["diff", "-a", "-u", "-I", "~~ERROR", expected_file, outfile], stdout = f_handle, stderr = f_handle)
#         else:
#             if sys.platform.startswith("win"):
#                 proc = subprocess.run(args = ["fc", expected_file, outfile], stdout = f_handle, stderr = f_handle)
#             else:
#                 proc = subprocess.run(args = ["diff", "-a", "-u", expected_file, outfile], stdout = f_handle, stderr = f_handle)

# find_pattern_create("demo.txt")

def main():
    find_pattern_drop()
    find_inp_JDBC()
    find_patterns()
    #diff fil output left

if __name__=="__main__":
    main()
