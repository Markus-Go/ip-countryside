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
 * File: ip2country.h
 * Purpose: Header file for country lookup demo client 
 * Responsible: Michael Yaco
 * Primary Repository: http://ip-countryside.googlecode.com/svn/trunk/
 * Web Sites: http://code.google.com/p/ip-countryside/, www.iupr.org, www.dfki.de, 
 * 
*/

#ifndef CNLOOKUP_H_
#define CNLOOKUP_H_

#include <ctype.h>
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>
#include <set>

using namespace std;
#define LINE_LENGTH 600

class CnLookUp{
public:
    CnLookUp();
    virtual ~CnLookUp();
};

class DBEntries {
public:
    unsigned int ipFrom;
    unsigned int ipTo;
    string country;
};

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

unsigned int convertToInt ( vector < string > octet){
    unsigned int value =  0;
    value =  (atoi ( octet[0].c_str() ) * 16777216) +
        (atoi ( octet[1].c_str() ) * 65536) +
        (atoi ( octet[2].c_str() ) * 256) +
        atoi ( octet[3].c_str() );
    return value;
}

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

vector <struct keyValue> vConfigFile;

struct keyValue {
    string key;
    string value;
};

vector <struct keyValue> readConfig ( string sFileName ) {
    char cBuf [256];
    string str;
    vector <string> vStr;
    vector <struct keyValue> vValues;
    ifstream in (sFileName.c_str());
    if (!in ) {
        cout << sFileName << "Unable to open config file!\n";
        exit(1);
    }
    while ( !(in.getline(cBuf,LINE_LENGTH).eof()) ) {
        str = cBuf;
        struct  keyValue * entry = new struct keyValue;
        vStr = split( str,'=' );
        entry->key = vStr[0];
        entry->value = vStr[1];
        vValues.push_back( *entry );
    }
    return vValues;
}

string findValue( string key ) {
    string value = " ";
    for ( unsigned int i = 0; i < vConfigFile.size(); i++ ) {
        if ( key == vConfigFile[i].key ) {
            return value = vConfigFile[i].value;
        }
    }
    cout << "Key not found in ConfigFile: "<< key << " . Stop."  << endl;
    exit(1);
}

#endif /*CNLOOKUP_H_*/
