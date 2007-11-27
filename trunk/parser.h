/**
 * Copyright 2007 Deutsches Forschungszentrum fuer Kuenstliche Intelligenz 
 * or its licensors, as applicable.
 *
 * You may not use this file except under the terms of the accompanying license.
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * 
 * Project: ip-countryside
 * File: parser.h
 * Purpose: Header file for building the ip2country database
 * Responsible: Michael Yaco
 * Primary Repository: http://ip-countryside.googlecode.com/svn/trunk/
 * Web Sites: http://code.google.com/p/ip-countryside/, www.iupr.org, www.dfki.de
 * 
*/

#ifndef PARSER_H_
#define PARSER_H_

#include <ctype.h>
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <list>
#include <vector>
#include <deque>
#include <set>


using namespace std;
#define LINE_LENGTH 600

void dbParser( string dbIn , string delName, string dbOut );
void delegParser( string , string );

//  contains a range with country [124.10.187.65-124.30.121.12-JP] 
class DBEntries {
public:
    unsigned int ipFrom;
    unsigned int ipTo;
    char country[2];
};

//  contains a range with country and registry [124.10.187.65-124.30.121.12-JP-APNIC] 
class DBRangeEntries {
public:
    unsigned int ipFrom;
    unsigned int ipTo;
    char country[2];
    string registry;
};

//    conatins single ip-country [124.12.10.122-AU]
struct net {
    char country[2];
    unsigned int ip;
    unsigned int size;
    bool bSetFlag;
};

//    conatins a delegation file range [124/8] = [124.0.0.0-124.255.255.255]
struct range {
    unsigned int ipFrom;
    unsigned int ipTo;
};

/*
 * the comp structure define the sorting strategy.
 * is used in combination with Set(Associative Container) to sort the elements 
 * in the set based on the range size of the elements.  
*/
struct comp {
    bool operator () ( const DBEntries e, const DBEntries e1 ) const  {
        if ( (e.ipTo - e.ipFrom) == (e1.ipTo - e1.ipFrom) )
            return (e.ipFrom <= e1.ipFrom);
        else
            return  ((e.ipTo - e.ipFrom) < (e1.ipTo - e1.ipFrom) );
    }
};
/*
 * the compare structure define the sorting strategy.
 * is used in combination with Set to sort the elements 
 * in the Set based on 1. ipFrom value if ipFrom is the same 2.based 
 * on ipTo.  
*/
struct compare {
    bool operator () ( const DBRangeEntries e, const DBRangeEntries e1 ) const {
        if ( e.ipFrom == e1.ipFrom ) {
            if ( e.ipTo == e1.ipTo ) {
                if ( (e.country[0] == e1.country[0]) && 
                     ( e.country[1] == e1.country[1] ))
                    return false;
                else
                    return true;
            }
            else
                return (e.ipTo <= e1.ipTo);
        }
        else
            return  ( e.ipFrom < e1.ipFrom );
    }
};

struct compare_entries {
    bool operator () ( const DBEntries e, const DBEntries e1 ) const {
        if ( e.ipFrom == e1.ipFrom ) {
            if ( e.ipTo == e1.ipTo ) {
                if ( (e.country[0] == e1.country[0]) && 
                     ( e.country[1] == e1.country[1] ))
                    return false;
                else
                    return true;
            }
            else
                return (e.ipTo <= e1.ipTo);
        }
        else
            return  ( e.ipFrom < e1.ipFrom );
    }
};

struct compare_structure {
    bool operator () ( const struct range e, const struct range e1 ) const {
        if ( e.ipFrom == e1.ipFrom ) {
            if ( e.ipTo == e1.ipTo ) {
                return false;
            }
            else
                return (e.ipTo <= e1.ipTo);
        }
        else
            return  ( e.ipFrom < e1.ipFrom );
    }
};

// Tests if this string starts with the specified prefix
int startWith( string sString ,string sValue ) {
    string::size_type loc;
    loc = sString.find(sValue,0);
    if ( loc == 0 )     
        return 1;
    else 
        return 0;
}

// Tests if this string contain the specified string

int contain( string sString ,string sValue ) {
    string::size_type loc;
    loc = sString.find(sValue,0);
    if ( loc != string::npos )    
        return 1;
    else 
        return 0;
}

//  Splits this string around matches of the given character
vector <string> split ( string sStr, char  cValue ) {
    string sString ;
    vector < string > vStr ;
    istringstream iss(sStr);
    size_t pos;
    while ( getline(iss, sString, cValue) ) {
        while( (pos = sString.find('\t')) != string::npos) {
            sString = sString.substr(0,pos) + sString.substr(pos+1);   
        }
        vStr.push_back(sString);
    }
    return vStr;
}

// Returns a copy of the string, with no whitespace.
string trim( string str ) {
    size_t pos;
    while( (pos = str.find(' ')) != string::npos) {
        str = str.substr(0,pos) + str.substr(pos+1);   
    }
    return str;
}

// Convert an IP of dot format to an integer value
unsigned int convertToInt ( vector < string > octet) {
    unsigned int value =  0;
    value =  (atoi ( octet[0].c_str() ) * 16777216) +
    (atoi ( octet[1].c_str() ) * 65536) +
    (atoi ( octet[2].c_str() ) * 256) +
    atoi ( octet[3].c_str() );
    return value;
}

// Convert an integer value to a dotted IP format
string convertIP( unsigned int ip ) {
    stringstream str;
    unsigned int oct1 = 0, oct2 = 0, oct3 = 0, oct4 = 0;
    oct1 = (ip / 16777216);
    ip %= 16777216;
    oct2 = (ip / 65536);
    ip %= 65536;
    oct3 = (ip / 256);
    ip %= 256;
    oct4 = ip;
    str << oct1 << "."<<oct2<<"."<<oct3<<"."<<oct4;
    return str.str();
}

// Converts all of the characters in this String to upper case.
string stringToUpper ( string str ) {
    for ( unsigned int i = 0 ; i < str.size() ; i++ ) {
        str[i] = toupper( str[i] );
    }
    return str;
}

// this vector contains the files path
vector <struct keyValue> vConfigFile;
// Holds the key-value pairs of the path
struct keyValue {
    string key;
    string value;    
};

// read the configFile 
vector <struct keyValue> readConfig ( string sFileName ) {
//    cout << "start reading config file \n";
    char cBuf [256];
    string str;
    vector <string> vStr;
    vector <struct keyValue> vValues;
    ifstream in (sFileName.c_str());
    if (!in ) {
        cout << sFileName << " File can NOT be opened ! \n";
        exit(1);
    }
    while ( !(in.getline(cBuf,LINE_LENGTH).eof())  ) {
        str = cBuf;
        struct  keyValue * entry = new struct keyValue;
        
        vStr = split( str,'=' );
        entry->key = vStr[0];
        entry->value = vStr[1];
        vValues.push_back( *entry );    
    }
    return vValues;        
}
// look for a key in the configFile 
string findValue( string key ) {
    string value = " ";
    for ( unsigned int i = 0; i < vConfigFile.size(); i++ ) {
        if ( key == vConfigFile[i].key ) {
            return value = vConfigFile[i].value;    
        }    
    }
    cout << key << " This is invalid key \n";
    exit(1);
}
class Parser {
public:
    Parser();
    virtual ~Parser();
};

#endif /*PARSER_H_*/



