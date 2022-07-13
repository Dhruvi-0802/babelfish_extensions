from datetime import datetime
import logging
from utils.db_client import Db_Client_psycopg
from pathlib import Path
import sys
import subprocess

def get_dependencies(file, logger):

    bbl_cnxn = Db_Client_psycopg('localhost', 'jdbc_testdb', 'jdbc_user', logger)

    try:
        curs2 = bbl_cnxn.get_cursor()
        curs2.close()
    except Exception as e:
        logger.error(str(e))

    try: 
        with open(file, "w") as expected_file:
            bbl_cursor = bbl_cnxn.get_cursor()
            # get user defined views dependent on sys views
            logger.info('\nSys views : ')
            query = """SELECT d.refobjid, d.refobjid::regclass, count(distinct v.oid) AS total_count 
                FROM pg_depend AS d 
                JOIN pg_rewrite AS r ON r.oid = d.objid  
                JOIN pg_class AS v ON v.oid = r.ev_class 
                WHERE d.classid = 'pg_rewrite'::regclass 
                    AND d.refclassid = 'pg_class'::regclass 
                    AND d.deptype in('n') 
                    AND d.refobjid in (SELECT oid FROM pg_class where relkind = 'v' and relnamespace = 'sys'::regnamespace)
                    AND v.relnamespace not in('sys'::regnamespace, 'pg_catalog'::regnamespace, 'information_schema_tsql'::regnamespace, 'information_schema'::regnamespace)
                GROUP BY d.refobjid; """
            bbl_cursor.execute(query)
            result = bbl_cursor.fetchall()
            for i in result:
                expected_file.write("Views {0} {1}\n".format(i[1],i[2]))
                logger.info(i)

            logger.info('\nsys Functions : ')
            # get user defined views dependent on sys functions 

            query = """SELECT id, id::regproc AS obj_name, sum(total_count) as dep_count 
                FROM
                (   (   SELECT d.refobjid AS id, d.refobjid::regproc, count(distinct v.oid) AS total_count 
                        FROM pg_depend AS d 
                        JOIN pg_rewrite AS r ON r.oid = d.objid
                        JOIN pg_class AS v ON v.oid = r.ev_class
                        WHERE d.classid = 'pg_rewrite'::regclass
                            AND d.refclassid = 'pg_proc'::regclass 
                            AND d.deptype in('n') 
                            AND d.refobjid in (SELECT oid FROM pg_proc where prokind = 'f' and pronamespace = 'sys'::regnamespace)
                            AND v.relnamespace not in('sys'::regnamespace, 'pg_catalog'::regnamespace, 'information_schema_tsql'::regnamespace, 'information_schema'::regnamespace)
                        GROUP BY d.refobjid
                    )
                    UNION ALL
                    (   SELECT d.refobjid, d.refobjid::regproc, count(distinct v.oid) AS total_count 
                        FROM pg_depend AS d 
                        JOIN pg_class AS v on v.oid = d.objid 
                        WHERE d.refclassid = 'pg_proc'::regclass 
                            AND d.deptype in ('a')
                            AND d.refobjid in (SELECT oid FROM pg_proc where prokind = 'f' and pronamespace = 'sys'::regnamespace)
                            AND v.relnamespace not in ('sys'::regnamespace, 'pg_catalog'::regnamespace, 'information_schema_tsql'::regnamespace, 'information_schema'::regnamespace)
                        GROUP BY d.refobjid
                    )
                ) AS temp GROUP BY id;"""       
            bbl_cursor.execute(query)

            result = bbl_cursor.fetchall()
            for i in result:
                expected_file.write("Functions {0} {1}\n".format(i[1],i[2]))
                logger.info(i)


            logger.info('\nsys operators : ')
            # get user defined views dependent on sys operators      
            query = """SELECT id, id::regoperator AS obj_name, sum(total_count) AS dep_count 
                FROM
                (   (   SELECT d.refobjid AS id, d.refobjid::regoperator, count(distinct v.oid) AS total_count 
                        FROM pg_depend AS d 
                        JOIN pg_rewrite AS r ON r.oid = d.objid
                        JOIN pg_class AS v ON v.oid = r.ev_class
                        WHERE d.classid = 'pg_rewrite'::regclass
                            AND d.refclassid = 'pg_operator'::regclass 
                            AND d.deptype in('n') 
                            AND d.refobjid in (SELECT oid FROM pg_operator where oid > 16384)
                            AND v.relnamespace not in('sys'::regnamespace, 'pg_catalog'::regnamespace, 'information_schema_tsql'::regnamespace, 'information_schema'::regnamespace)
                        GROUP BY refobjid
                    )
                        UNION ALL
                    (   SELECT d.refobjid, d.refobjid::regoperator, count(distinct v.oid) AS total_count 
                        FROM pg_depend AS d 
                        JOIN pg_class AS v on v.oid = d.objid 
                        WHERE d.refclassid = 'pg_operator'::regclass 
                            AND d.deptype in ('a')
                            AND d.refobjid in (select oid FROM pg_operator where oid > 16384)
                            AND v.relnamespace not in ('sys'::regnamespace, 'pg_catalog'::regnamespace, 'information_schema_tsql'::regnamespace, 'information_schema'::regnamespace)
                        GROUP BY d.refobjid
                    )
                ) AS temp GROUP BY id;"""  
            bbl_cursor.execute(query)

            result = bbl_cursor.fetchall()
            for i in result:
                expected_file.write("Operators {0} {1}\n".format(i[1],i[2]))
                logger.info(i)


            logger.info('\nsys types : ')
            # get user defined views & tables, union functions & procedures, union types dependent on sys types  
            query = """SELECT id, id::regtype AS obj_name, sum(total_count) AS dep_count 
                FROM
                (   (   SELECT d.refobjid AS id, d.refobjid::regtype, count(distinct v.oid) AS total_count 
                        FROM pg_depend AS d 
                        JOIN pg_class AS v on v.oid = d.objid 
                        WHERE d.refclassid = 'pg_type'::regclass 
                            AND d.deptype in ('n')
                            AND d.refobjid in (SELECT oid FROM pg_type WHERE typnamespace = 'sys'::regnamespace AND typtype in ('b','d') AND typcategory <> 'A')
                            AND v.relnamespace not in ('sys'::regnamespace, 'pg_catalog'::regnamespace, 'information_schema_tsql'::regnamespace, 'information_schema'::regnamespace)
                        GROUP BY d.refobjid
                    )
                        UNION ALL
                    (   SELECT d.refobjid, d.refobjid::regtype, count(distinct v.oid) AS total_count 
                        FROM pg_depend AS d 
                        JOIN pg_proc AS v on v.oid = d.objid 
                        WHERE d.refclassid = 'pg_type'::regclass 
                            AND d.deptype in ('n')
                            AND d.refobjid in (SELECT oid FROM pg_type WHERE typnamespace = 'sys'::regnamespace AND typtype in ('b','d') AND typcategory <> 'A')
                            AND v.pronamespace not in ('sys'::regnamespace, 'pg_catalog'::regnamespace, 'information_schema_tsql'::regnamespace, 'information_schema'::regnamespace)
                        GROUP BY d.refobjid
                    )
                        UNION ALL
                    (   SELECT d.refobjid, d.refobjid::regtype, count(distinct v.oid) AS total_count 
                        FROM pg_depend AS d 
                        JOIN pg_type AS v on v.oid = d.objid 
                        WHERE d.refclassid = 'pg_type'::regclass 
                        AND d.deptype in ('n')
                        AND d.refobjid in (SELECT oid FROM pg_type WHERE typnamespace = 'sys'::regnamespace AND typtype in ('b','d') AND typcategory <> 'A')
                        AND v.typnamespace not in ('sys'::regnamespace, 'pg_catalog'::regnamespace, 'information_schema_tsql'::regnamespace, 'information_schema'::regnamespace)
                        GROUP BY d.refobjid
                    )
                ) AS temp GROUP BY id;"""

            bbl_cursor.execute(query)
            result = bbl_cursor.fetchall()
            for i in result:
                expected_file.write("Types {0} {1}\n".format(i[1],i[2]))
                logger.info(i)

            logger.info('\nsys collations : ')
            # get user defined views,tables dependent on sys collations      
            query = """SELECT d.refobjid, d.refobjid::regcollation, count(distinct v.oid) AS total_count 
                FROM pg_depend AS d 
                JOIN pg_class AS v on v.oid = d.objid 
                WHERE d.refclassid = 'pg_collation'::regclass 
                    AND d.deptype in ('n')
                    AND d.refobjid in (SELECT oid FROM pg_collation where collnamespace = 'sys'::regnamespace)
                    AND v.relnamespace not in ('sys'::regnamespace, 'pg_catalog'::regnamespace, 'information_schema_tsql'::regnamespace, 'information_schema'::regnamespace)
                GROUP BY d.refobjid;"""  
            bbl_cursor.execute(query)
            result = bbl_cursor.fetchall()
            for i in result:
                expected_file.write("Collations {0} {1}\n".format(i[1],i[2]))
                logger.info(i)


    except Exception as e:
        logger.info(str(e))



# compare the generated and expected file using diff
def compare_outfiles(outfile, expected_file, logfname, filename, logger):
    try:
        diff_file = Path.cwd().joinpath("logs", logfname, "sql_validation", filename + ".diff")
        f_handle = open(diff_file, "wb")

        # sorting the files as set will give unordered outputs
        if sys.platform.startswith("win"):
            proc_sort = subprocess.run(args = ["sort", expected_file, "/o", expected_file])
            proc_sort = subprocess.run(args = ["sort", outfile, "/o", outfile])
            proc = subprocess.run(args = ["fc", expected_file, outfile], stdout = f_handle, stderr = f_handle)
        else:
            proc_sort = subprocess.run(args = ["sort", "-o", expected_file, expected_file])
            proc_sort = subprocess.run(args = ["sort", "-o", outfile, outfile])
            proc = subprocess.run(args = ["diff", "-a", "-u", "-I", "~~ERROR", expected_file, outfile], stdout = f_handle, stderr = f_handle)
        
        rcode = proc.returncode
        f_handle.close()
        
        # adding logs based on the returncode of diff command
        if rcode == 0:
            logger.info("No difference found!")
            return True
        elif rcode ==  1:
            with open(diff_file, "r") as f:
                logger.info("\n" + f.read())
            return False
        elif rcode == 2:
            with open(diff_file, "r") as f:
                logger.info("\n" + f.read())
            logger.error("Some error occured while executing the diff command!")
            return False
        else:
            logger.error("Unknown exit code encountered while running diff!")
            return False
        
    except Exception as e:
        logger.error(str(e))
    
    return False


# set up logger for the framework
def create_logger():

    # set up path for logger
    log_folder_name = datetime.now().strftime('log_%H_%M_%d_%m_%Y')
    path = Path.cwd().joinpath("logs", log_folder_name)
    Path.mkdir(path, parents = True, exist_ok = True)

    filename = "sql_validation"
    logname = datetime.now().strftime(filename + '_%H_%M_%d_%m_%Y.log')

    path = Path.cwd().joinpath("logs", log_folder_name, filename)
    Path.mkdir(path, parents = True, exist_ok = True)

    # creating logger with two handlers, file as well as console
    # file logger
    file_path = path.joinpath(logname)

    fh = logging.FileHandler(filename = file_path, mode = "w")
    formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(message)s')
    fh.setFormatter(formatter)
    logger = logging.getLogger(filename)
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)

    # console logger
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    logger.setLevel(logging.DEBUG)

    return log_folder_name, logger


# remove and close log handlers
def close_logger(logger):
    if logger is None:
        return
    else:
        for handler in list(logger.handlers):
            logger.removeHandler(handler) 
            handler.close()


def main():

    logfname, logger = create_logger()
    
    file_name = "dependency_check"
    
    expected_file = Path.cwd().joinpath("expected", "sql_validation_framework", file_name + ".out")
    outfile = Path.cwd().joinpath("output", "sql_validation_framework", file_name + ".out")
    get_dependencies(outfile, logger)
    
    result2 = compare_outfiles(outfile, expected_file, logfname, file_name, logger)

    try:
        assert result2 == True
        logger.info("Test Passed!")
    except AssertionError as e:
        logger.error("Test Failed!")

    close_logger(logger)

    assert result2 == True

if __name__ == "__main__":
    main()
