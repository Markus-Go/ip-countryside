from ip_countryside_db import *
from ip_countryside_parser import *


if __name__ == "__main__":   

    # @TODOs
    # 05. Code aufräumen und Methods documentieren
    # 06. Spliting Records to find overlaps Strategy dokumentieren
    # 07. Update README.md
    # 08. Update run.ps1

    run_parser(multicore=True)

    # create sqlite for website
    extract_as_sqllite()

    extract_as_mysql()
    extract_as_json()
    extract_as_yaml()
    
    split_db()
    