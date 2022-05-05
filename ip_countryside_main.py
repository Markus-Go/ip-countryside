from ip_countryside_db import extract_as_json, extract_as_mmdb, extract_as_mmdb_fast, extract_as_mysql, extract_as_sqllite, extract_as_yaml


if __name__ == "__main__":   

    # @TODOs
    # 05. Code aufräumen und Methods documentieren
    # 06. Spliting Records to find overlaps Strategy dokumentieren
    # 07. Update README.md
    # 08. Update run.ps1
    # 09. Optimize downloader script

    #run_parser(multicore=True)

    # create sqlite for website

    extract_as_sqllite()
