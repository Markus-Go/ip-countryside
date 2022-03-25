import os

# PATHS
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DEL_FILES_DIR = os.path.join(ROOT_DIR, "del_files")

MERGED_DEL_FILE        = os.path.join(DEL_FILES_DIR, "merged_del_file.txt")
STRIPPED_DEL_FILE      = os.path.join(DEL_FILES_DIR, "stipped_del_file.txt")

# Regex for matching ip versions
IPV4_PATTERN = "[0-9]+(?:\.[0-9]+){3}"
IPV6_PATTERN = "(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"

# RIAS information
AFRINIC = {
    'host':         "ftp.afrinic.net",
    'cwd':          "pub/stats/afrinic/",
    'fname':        "delegated-afrinic-latest"
}

LACNIC = {
    'host':         "ftp.lacnic.net",
    'cwd':          "pub/stats/lacnic/",
    'fname':        "delegated-lacnic-latest"
}

ARIN = {
    'host':         "ftp.arin.net",
    'cwd':          "pub/stats/arin/",
    'fname':        "delegated-arin-extended-latest"
}

APNIC = {
    'host':         "ftp.apnic.net",
    'cwd':          "pub/stats/apnic/",
    'fname':        "delegated-apnic-latest",
    'splitcwd':     "/apnic/whois/",
    'splitfname':   "apnic.db.inetnum.gz",
}

RIPE = {
    'host':         "ftp.ripe.net",
    'cwd':          "ripe/stats/",
    'fname':        "delegated-ripencc-latest",
    'splitcwd':     "/ripe/dbase/split/",
    'splitfname':   "ripe.db.inetnum.gz",
}


COUNTRY_DICTIONARY = {
    'AF':"AFGHANISTAN",
    'AX':"ÅLAND ISLANDS",
    'AL':"ALBANIA",
    'DZ':"ALGERIA",
    'AS':"AMERICAN SAMOA",
    'AD':"ANDORRA",
    'AO':"ANGOLA",
    'AI':"ANGUILLA",
    'AQ':"ANTARCTICA",
    'AG':"ANTIGUA AND BARBUDA",
    'AR':"ARGENTINA",
    'AM':"ARMENIA",
    'AW':"ARUBA",
    'AP':"ASIA-PACIFIC (NO-COUNTRY-ASSIGNED)",
    'AU':"AUSTRALIA",
    'AT':"AUSTRIA",
    'AZ':"AZERBAIJAN",
    'BS':"BAHAMAS",
    'BH':"BAHRAIN",
    'BD':"BANGLADESH",
    'BB':"BARBADOS",
    'BY':"BELARUS",
    'BE':"BELGIUM",
    'BZ':"BELIZE",
    'BJ':"BENIN",
    'BM':"BERMUDA",
    'BT':"BHUTAN",
    'BO':"BOLIVIA",
    'BQ':"BONAIRE, SAINT EUSTATIUS AND SABA",
    'BA':"BOSNIA AND HERZEGOVINA",
    'BW':"BOTSWANA",
    'BV':"BOUVET ISLAND",
    'BR':"BRAZIL",
    'IO':"BRITISH INDIAN OCEAN TERRITORY",
    'BN':"BRUNEI DARUSSALAM",
    'BG':"BULGARIA",
    'BF':"BURKINA FASO",
    'BI':"BURUNDI",
    'KH':"CAMBODIA",
    'CM':"CAMEROON",
    'CA':"CANADA",
    'CV':"CAPE VERDE",
    'KY':"CAYMAN ISLANDS",
    'CF':"CENTRAL AFRICAN REPUBLIC",
    'TD':"CHAD",
    'CL':"CHILE",
    'CN':"CHINA",
    'CX':"CHRISTMAS ISLAND",
    'CC':"COCOS (KEELING) ISLANDS",
    'CO':"COLOMBIA",
    'KM':"COMOROS",
    'CG':"CONGO",
    'CD':"CONGO, THE DEMOCRATIC REPUBLIC OF THE",
    'CK':"COOK ISLANDS",
    'CR':"COSTA RICA",
    'CI':"CÔTE D'IVOIRE",
    'HR':"CROATIA",
    'CU':"CUBA",
    'CW':"CURACAO",
    'CY':"CYPRUS",
    'CZ':"CZECH REPUBLIC",
    'DK':"DENMARK",
    'DJ':"DJIBOUTI",
    'DM':"DOMINICA",
    'DO':"DOMINICAN REPUBLIC",
    'EC':"ECUADOR",
    'EG':"EGYPT",
    'SV':"EL SALVADOR",
    'GQ':"EQUATORIAL GUINEA",
    'ER':"ERITREA",
    'EE':"ESTONIA",
    'ET':"ETHIOPIA",
    'EU':"EUROPE (NO-COUNTRY-ASSIGNED)",
    'FK':"FALKLAND ISLANDS (MALVINAS)",
    'FO':"FAROE ISLANDS",
    'FJ':"FIJI",
    'FI':"FINLAND",
    'FR':"FRANCE",
    'GF':"FRENCH GUIANA",
    'PF':"FRENCH POLYNESIA",
    'TF':"FRENCH SOUTHERN TERRITORIES",
    'GA':"GABON",
    'GM':"GAMBIA",
    'GE':"GEORGIA",
    'DE':"GERMANY",
    'GH':"GHANA",
    'GI':"GIBRALTAR",
    'GR':"GREECE",
    'GL':"GREENLAND",
    'GD':"GRENADA",
    'GP':"GUADELOUPE",
    'GU':"GUAM",
    'GT':"GUATEMALA",
    'GG':"GUERNSEY",
    'GW':"GUINEA-BISSAU",
    'GN':"GUINEA",
    'GY':"GUYANA",
    'HT':"HAITI",
    'HM':"HEARD ISLAND AND MCDONALD ISLANDS",
    'VA':"HOLY SEE (VATICAN CITY STATE)",
    'HN':"HONDURAS",
    'HK':"HONG KONG",
    'HU':"HUNGARY",
    'IS':"ICELAND",
    'IN':"INDIA",
    'ID':"INDONESIA",
    'IR':"IRAN, ISLAMIC REPUBLIC OF",
    'IQ':"IRAQ",
    'IE':"IRELAND",
    'IM':"ISLE OF MAN",
    'IL':"ISRAEL",
    'IT':"ITALY",
    'JM':"JAMAICA",
    'JP':"JAPAN",
    'JE':"JERSEY",
    'JO':"JORDAN",
    'KZ':"KAZAKHSTAN",
    'KE':"KENYA",
    'KI':"KIRIBATI",
    'KP':"KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF",
    'KR':"KOREA, REPUBLIC OF",
    'KW':"KUWAIT",
    'KG':"KYRGYZSTAN",
    'LA':"LAO PEOPLE'S DEMOCRATIC REPUBLIC",
    'LV':"LATVIA",
    'LB':"LEBANON",
    'LS':"LESOTHO",
    'LR':"LIBERIA",
    'LY':"LIBYAN ARAB JAMAHIRIYA",
    'LI':"LIECHTENSTEIN",
    'LT':"LITHUANIA",
    'LU':"LUXEMBOURG",
    'MO':"MACAO",
    'MK':"MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF",
    'MG':"MADAGASCAR",
    'MW':"MALAWI",
    'MY':"MALAYSIA",
    'MV':"MALDIVES",
    'ML':"MALI",
    'MT':"MALTA",
    'MH':"MARSHALL ISLANDS",
    'MQ':"MARTINIQUE",
    'MR':"MAURITANIA",
    'MU':"MAURITIUS",
    'YT':"MAYOTTE",
    'MX':"MEXICO",
    'FM':"MICRONESIA, FEDERATED STATES OF",
    'MD':"MOLDOVA, REPUBLIC OF",
    'MC':"MONACO",
    'MN':"MONGOLIA",
    'ME':"MONTENEGRO",
    'MS':"MONTSERRAT",
    'MA':"MOROCCO",
    'MZ':"MOZAMBIQUE",
    'MM':"MYANMAR",
    'NA':"NAMIBIA",
    'NR':"NAURU",
    'NP':"NEPAL",
    'AN':"NETHERLANDS ANTILLES",
    'NL':"NETHERLANDS",
    'NC':"NEW CALEDONIA",
    'NZ':"NEW ZEALAND",
    'NI':"NICARAGUA",
    'NG':"NIGERIA",
    'NE':"NIGER",
    'NU':"NIUE",
    'NF':"NORFOLK ISLAND",
    'MP':"NORTHERN MARIANA ISLANDS",
    'NO':"NORWAY",
    'OM':"OMAN",
    'PK':"PAKISTAN",
    'PW':"PALAU",
    'PS':"PALESTINIAN TERRITORY, OCCUPIED",
    'PA':"PANAMA",
    'PG':"PAPUA NEW GUINEA",
    'PY':"PARAGUAY",
    'PE':"PERU",
    'PH':"PHILIPPINES",
    'PN':"PITCAIRN",
    'PL':"POLAND",
    'PT':"PORTUGAL",
    'PR':"PUERTO RICO",
    'QA':"QATAR",
    'RE':"REUNION",
    'RO':"ROMANIA",
    'RU':"RUSSIAN FEDERATION",
    'RW':"RWANDA",
    'BL':"SAINT BARTHÉLEMY",
    'SH':"SAINT HELENA",
    'KN':"SAINT KITTS AND NEVIS",
    'LC':"SAINT LUCIA",
    'MF':"SAINT MARTIN",
    'PM':"SAINT PIERRE AND MIQUELON",
    'VC':"SAINT VINCENT AND THE GRENADINES",
    'WS':"SAMOA",
    'SM':"SAN MARINO",
    'ST':"SAO TOME AND PRINCIPE",
    'SA':"SAUDI ARABIA",
    'SN':"SENEGAL",
    'CS':"SERBIA AND MONTENEGRO",
    'RS':"SERBIA",
    'SC':"SEYCHELLES",
    'SL':"SIERRA LEONE",
    'SG':"SINGAPORE",
    'SX':"SINT MAARTEN (DUTCH PART)",
    'SK':"SLOVAKIA",
    'SI':"SLOVENIA",
    'SB':"SOLOMON ISLANDS",
    'SO':"SOMALIA",
    'ZA':"SOUTH AFRICA",
    'GS':"SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS",
    'SS':"SOUTH SUDAN",
    'ES':"SPAIN",
    'LK':"SRI LANKA",
    'SD':"SUDAN",
    'SR':"SURINAME",
    'SJ':"SVALBARD AND JAN MAYEN",
    'SZ':"SWAZILAND",
    'SE':"SWEDEN",
    'CH':"SWITZERLAND",
    'SY':"SYRIAN ARAB REPUBLIC",
    'TW':"TAIWAN, PROVINCE OF CHINA",
    'TJ':"TAJIKISTAN",
    'TZ':"TANZANIA, UNITED REPUBLIC OF",
    'TH':"THAILAND",
    'TL':"TIMOR-LESTE",
    'TG':"TOGO",
    'TK':"TOKELAU",
    'TO':"TONGA",
    'TT':"TRINIDAD AND TOBAGO",
    'TN':"TUNISIA",
    'TR':"TURKEY",
    'TM':"TURKMENISTAN",
    'TC':"TURKS AND CAICOS ISLANDS",
    'TV':"TUVALU",
    'UG':"UGANDA",
    'UA':"UKRAINE",
    'AE':"UNITED ARAB EMIRATES",
    'GB':"UNITED KINGDOM",
    'UM':"UNITED STATES MINOR OUTLYING ISLANDS",
    'US':"UNITED STATES",
    'UY':"URUGUAY",
    'UZ':"UZBEKISTAN",
    'VU':"VANUATU",
    'VE':"VENEZUELA",
    'VN':"VIET NAM",
    'VG':"VIRGIN ISLANDS, BRITISH",
    'VI':"VIRGIN ISLANDS, U.S.",
    'WF':"WALLIS AND FUTUNA",
    'EH':"WESTERN SAHARA",
    'EH':"WESTERN SAHARA",
    'YE':"YEMEN",
    'YU':"YUGOSLAVIA",
    'ZM':"ZAMBIA",
    'ZW':"ZIMBABWE"
}