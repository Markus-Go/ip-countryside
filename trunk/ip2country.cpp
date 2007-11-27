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
 * File: ip2country.cpp
 * Purpose: Country lookup demo client 
 * Responsible: Michael Yaco
 * Primary Repository: http://ip-countryside.googlecode.com/svn/trunk/
 * Web Sites: http://code.google.com/p/ip-countryside/, www.iupr.org, www.dfki.de, 
 * 
*/



#include "ip2country.h"

int main(int argc, char* argv[]){
    vConfigFile = readConfig( "config" );
    char cBuf[LINE_LENGTH];
    vector <string> sIP;
    vector <DBEntries> vRanges;
    vector <string> sEntry;
    string sStr , sStr1, errorStr;
    bool bMatch = false;

    ifstream in ( (findValue("IpToCountry")).c_str() );
    if (!in ) {
        cout << "Database file " << (findValue("IpToCountry")).c_str() << " could not be found! \n";
        return 1;
    }

   if ( argc < 2 ) {
        cout << "Usage: " <<  argv[0] << " <query-ip>" << endl;
        return 1;    
    }
    sStr1 = argv[1];
    errorStr = "Please enter a valid IP address.\n";
    int iDotNum = 0, iDigitNum = 0;
    for (uint i = 0; i < sStr1.length(); i++ ) {
        if ( isdigit (sStr1[i]) ) {
            iDigitNum++;
            if ( iDigitNum > 3 ) {
                cout << errorStr;
                return 1;
            }
        }
        else if ( sStr1[i] == '.' ) {
            iDotNum++;
            if ( iDigitNum == 0 || iDigitNum > 3 ) {
                cout << errorStr;
                return 1;
            }
            iDigitNum = 0;
            if ( iDotNum == 3 ) {
                if ( i ==  sStr1.length()-1 ) {
                    cout << errorStr;
                    return 1;    
                }
            }
        }
        else if ( isalpha(sStr1[i]) ) {
            cout << errorStr;
            return 1;
        }
    }
    if ( iDotNum != 3 ) {
        cout << errorStr;
        return 1;
    }
    sIP = split( sStr1 , '.' );
    if (! ( (atoi(sIP[0].c_str()) >= 0 && atoi(sIP[0].c_str()) <= 255)) ||  
        ( !(atoi(sIP[1].c_str()) >= 0 && atoi(sIP[1].c_str()) <= 255)) ||
        ( !(atoi(sIP[2].c_str()) >= 0 && atoi(sIP[2].c_str()) <= 255)) ||
        ( !(atoi(sIP[3].c_str()) >= 0 && atoi(sIP[3].c_str()) <= 255)) ){
       cout << errorStr;
       return 1; 
    }

    stringstream sstream;
    while ( !(in.getline(cBuf,LINE_LENGTH).eof())  ) {
        sEntry.clear();
        sStr = cBuf;
        if( !sStr.empty() ) {
            sEntry = split( sStr , ' ' );
            DBEntries *sRange = new DBEntries();
            sstream.clear();
            sstream << sEntry[0];
            sstream >> sRange->ipFrom;
            sstream.clear();
            sstream << sEntry[1];
            sstream >> sRange->ipTo;
            sRange->country = sEntry[2];
            vRanges.push_back( *sRange );
        }
    }
    unsigned int ip = 0;
    ip = convertToInt( sIP );
    int lowerb = 0 , upperb = vRanges.size()-1,mid = 0; 

    while ( lowerb <= upperb ) {
        mid = ( lowerb + upperb ) / 2;
        if(vRanges[mid].ipFrom <= ip && vRanges[mid].ipTo >= ip ) {
            cout << convertIP(vRanges[mid].ipFrom) << "-" << convertIP(vRanges[mid].ipTo)
            << "-" << vRanges[mid].country << endl;
            cout<< convertIP(ip) << " " << vRanges[mid].country << endl;
            bMatch = true;
            break;
        }
        else if(vRanges[mid].ipTo < ip) {
            lowerb = mid + 1;
        }
        else if( vRanges[mid].ipFrom > ip ) {
            upperb = mid - 1;
        }
    }

    if (! bMatch) {
        cout << convertIP(ip) << " " << "Unknown" << endl;
    }
    bMatch = false;
    in.close();
    return 0;
}
