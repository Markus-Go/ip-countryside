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
 * File: parser.cpp
 * Purpose: source file for building the ip2country database
 * Responsible: Markus Goldstein
 * Primary Repository: http://ip-countryside.googlecode.com/svn/trunk/
 * Web Sites: http://code.google.com/p/ip-countryside/, www.iupr.org, www.dfki.de, 
 * 
*/

#include "parser.h"

int main() {
    vConfigFile = readConfig( "config" );
    // clears files from old values
    ofstream inDBex ( (findValue("DBout")).c_str() );
    inDBex.close();
    ofstream inDBex1 ( (findValue("Testout")).c_str()  );
    inDBex1.close();

    char cBuf[LINE_LENGTH];
    stringstream sstream;
    string sStr;
    unsigned int temp = 0;

    set < DBRangeEntries , compare > seEntries;
    set < DBEntries , compare_entries > setEntries;
    vector <string>  sEntry;
    vector < DBRangeEntries > vDBEntries;
    vector < DBEntries > vEntries;

    // All delegation files are parsed and merged to one file 
    delegParser( "afrinic" , "Testout" );
    delegParser( "lacnic" , "Testout" );
    delegParser( "arin" , "Testout" );
    delegParser( "apnic" , "Testout" );
    delegParser( "ripencc" , "Testout" );

    ifstream inDel ( (findValue("Testout")).c_str() );
    if (!inDel ) {
        cout <<"Testout  File can NOT be opened ! \n";
        return 1;
    }
    ofstream outDel ( (findValue("DBout")).c_str(), ios::app );

    // read the Parsed delegation files to set, the set sorts the entries based on ipFrom then on ipTo 
    while ( !(inDel.getline(cBuf,LINE_LENGTH).eof())  ) {
        sStr = cBuf;
        if ( !sStr.empty() ) {
            DBRangeEntries entry;
            sstream.clear();
            sStr = cBuf;
            sEntry = split ( sStr , '-' );
            sstream << sEntry[0];
            sstream >> temp;
            entry.ipFrom = temp;
            sstream.clear();
            sstream << sEntry[1];
            sstream >> temp;
            entry.ipTo = temp;
            entry.country[0] = sEntry[2][0];
            entry.country[1] = sEntry[2][1];
            entry.registry = string(sEntry[3]);

            seEntries.insert(entry);
        }
    }

    set <DBRangeEntries , compare>::iterator it;   
    for ( it = seEntries.begin(); it != seEntries.end(); it++ ) {
        vDBEntries.push_back(*it);
    }
    // clear the set
    seEntries.clear();    
    
    unsigned int uDBsize = vDBEntries.size();

    // check for overlaps between delegation files.     
    for ( unsigned int i = 0 ; i < uDBsize -1  ; i++ ) {
        if ( vDBEntries[i+1].ipFrom > vDBEntries[i].ipTo ) {
            continue;
        }
        else if ( vDBEntries[i+1].ipFrom <= vDBEntries[i].ipTo ) {
            // if the cause of the conflict is ripencc then change ripencc 
            // entry to remove the confilct
            if ( (vDBEntries[i].registry == "ripencc" ) || 
               ( vDBEntries[i+1].registry == "ripencc" )) {
                if ( vDBEntries[i].registry == "ripencc" ) {
                    if ( (vDBEntries[i].ipFrom == vDBEntries[i+1].ipFrom) &&
                            ( ( vDBEntries[i].ipTo == vDBEntries[i+1].ipTo ) || 
                            ( vDBEntries[i].ipTo < vDBEntries[i+1].ipTo ) )  ) {
                        vDBEntries[i].registry = "XX";
                    }
                    else if ( (vDBEntries[i].ipFrom < vDBEntries[i+1].ipFrom) && 
                            (( vDBEntries[i].ipTo == vDBEntries[i+1].ipTo ) || 
                            ( (vDBEntries[i].ipTo >= vDBEntries[i+1].ipFrom)&& 
                            (vDBEntries[i].ipTo <= vDBEntries[i+1].ipTo)  ) ) ) {
                        vDBEntries[i].ipTo = vDBEntries[i+1].ipFrom - 1;

                    }
                    else if ( (vDBEntries[i].ipFrom < vDBEntries[i+1].ipFrom) && 
                    ( vDBEntries[i].ipTo > vDBEntries[i+1].ipTo ) ) {
                        DBRangeEntries entry;

                        entry.ipFrom = vDBEntries[i+1].ipTo + 1;
                        entry.ipTo = vDBEntries[i].ipTo;
                        entry.country[0] = vDBEntries[i].country[0];
                        entry.country[1] = vDBEntries[i].country[1];
                        entry.registry = vDBEntries[i].registry;

                        vDBEntries.push_back(entry);
                        vDBEntries[i].ipTo = vDBEntries[i+1].ipFrom - 1;
                    }
                }
                else {
                    if ( (vDBEntries[i].ipFrom <= vDBEntries[i+1].ipFrom) && 
                         ( vDBEntries[i].ipTo >= vDBEntries[i+1].ipTo )  ) {
                        vDBEntries[i+1].registry = "XX";
                    }
                    else if ( (vDBEntries[i].ipFrom <= vDBEntries[i+1].ipFrom) &&
                              (vDBEntries[i].ipTo >= vDBEntries[i+1].ipFrom) && 
                              ( vDBEntries[i].ipTo < vDBEntries[i+1].ipTo )  ) {
                        vDBEntries[i+1].ipFrom = vDBEntries[i].ipTo + 1;
                    }
                }

            }

            else {
                // if the conflict is between entries except ripe then the change is made on the
                // first entry that cause the conflict
                if ( (vDBEntries[i].ipFrom == vDBEntries[i+1].ipFrom) &&
                     ( ( vDBEntries[i].ipTo == vDBEntries[i+1].ipTo ) || 
                     ( vDBEntries[i].ipTo < vDBEntries[i+1].ipTo ) )  ) {
                        vDBEntries[i].registry = "XX";
                    }
                    else if ( (vDBEntries[i].ipFrom < vDBEntries[i+1].ipFrom) && 
                            (( vDBEntries[i].ipTo == vDBEntries[i+1].ipTo ) || 
                            ( (vDBEntries[i].ipTo >= vDBEntries[i+1].ipFrom) && 
                            (vDBEntries[i].ipTo <= vDBEntries[i+1].ipTo)  ) ) ) {
                        vDBEntries[i].ipTo = vDBEntries[i+1].ipFrom - 1;

                    }
                    else if ( (vDBEntries[i].ipFrom < vDBEntries[i+1].ipFrom) && 
                              ( vDBEntries[i].ipTo > vDBEntries[i+1].ipTo ) ) {
                        DBRangeEntries entry;

                        entry.ipFrom = vDBEntries[i+1].ipTo + 1;
                        entry.ipTo = vDBEntries[i].ipTo;
                        entry.country[0] = vDBEntries[i].country[0];
                        entry.country[1] = vDBEntries[i].country[1];
                        entry.registry = vDBEntries[i].registry;

                        vDBEntries.push_back(entry);
                        vDBEntries[i].ipTo = vDBEntries[i+1].ipFrom - 1;
                    }
            }
        }
    }

    ofstream apnic ( (findValue("apnicDel")).c_str() );
    ofstream ripe ( (findValue("ripeDel")).c_str() );

    for ( unsigned int i = 0; i < vDBEntries.size() ; i++ ) {
        if ( vDBEntries[i].registry == "apnic" )
            apnic << vDBEntries[i].ipFrom << "-" << vDBEntries[i].ipTo <<  "-"
                  << vDBEntries[i].country << endl;
        else if ( vDBEntries[i].registry == "ripencc" )
            ripe << vDBEntries[i].ipFrom << "-" << vDBEntries[i].ipTo <<  "-"
                 << vDBEntries[i].country<< endl;
        else if ( vDBEntries[i].registry == "lacnic" )
            outDel << vDBEntries[i].ipFrom << "-" << vDBEntries[i].ipTo <<  "-"
                   << vDBEntries[i].country<< endl;
        else if ( vDBEntries[i].registry == "arin" )
            outDel << vDBEntries[i].ipFrom << "-" << vDBEntries[i].ipTo <<  "-"
                   << vDBEntries[i].country<< endl;
        else if ( vDBEntries[i].registry == "afrinic" )
            outDel << vDBEntries[i].ipFrom << "-" << vDBEntries[i].ipTo <<  "-"
                   << vDBEntries[i].country<< endl;
    }
    
    dbParser( "ripe.db.inetnum" , "ripe" , "DBout" );
    dbParser( "apnic.db.inetnum" , "apnic" , "DBout" );
    
    temp = 0;
    sstream.clear();
    sEntry.clear();
    
    ifstream inDB ( (findValue("DBout")).c_str() );
     if (!inDB ) {
        cout <<"DBout  File can NOT be opened ! \n";
        return 1;
    }
    ofstream outDB ( (findValue("IpToCountry")).c_str() );
    
    
    
    
    // read the final version of the delegation files to sort it.
    while ( !(inDB.getline(cBuf,LINE_LENGTH).eof())  ) {
        sStr = cBuf;
        if ( !sStr.empty() ) {
            DBEntries entry;
            sstream.clear();
            sStr = cBuf;
            sEntry = split ( sStr , '-' );
            sstream << sEntry[0];
            sstream >> temp;
            entry.ipFrom = temp;
            sstream.clear();
            sstream << sEntry[1];
            sstream >> temp;
            entry.ipTo = temp;
            entry.country[0] = sEntry[2][0];
            entry.country[1] = sEntry[2][1];
            
            setEntries.insert(entry);
        }
    }
    
    set <DBEntries , compare_entries>::iterator iter;   
    for ( iter = setEntries.begin(); iter != setEntries.end(); iter++ ) {
        vEntries.push_back(*iter);
    }
    // clear the set
    setEntries.clear();    
    
    uDBsize = vEntries.size();
    
    unsigned int from = vEntries[0].ipFrom;
    unsigned int to = vEntries[0].ipTo;
    for ( unsigned int i = 1 ; i < uDBsize -1  ; i++ ) {
        if (vEntries[i].ipFrom > to+1 || vEntries[i-1].country[0] != vEntries[i].country[0]
            || vEntries[i-1].country[1] != vEntries[i].country[1]) {
            outDB << from << " " << to << " " 
                  << vEntries[i-1].country[0] << vEntries[i-1].country[1]<< endl;
            from = vEntries[i].ipFrom;
            to = vEntries[i].ipTo;
        }
        else {
            to =  vEntries[i].ipTo;
        }
    }
    outDB << from << " " << to << " " 
          << vEntries[uDBsize-2].country[0] << vEntries[uDBsize-2].country[1]<< endl;

    inDB.close();
    outDB.close();
    apnic.close();
    ripe.close();
    
    // time_t current = time(0);
    
    cout << "Program Terminated!"<<endl;
    return 0;
}

// this function is used to process the apnic and ripe dbs, 
void dbParser( string dbIn , string delName, string dbOut ) {
    char cBuf[LINE_LENGTH];

    string sStr;
    vector <string>  sEntry;
    vector <string>  sStrArray;
    vector <string>  sIPFrom , sIPTo;
    vector < int > vEntries;  // contain indeces to the ranges in Database
    vector < DBEntries > vRanges;
    vector < DBEntries > vRangeIP;
    vector < DBEntries > vNets; 
    set < DBEntries , comp > seEntries;
    vector < DBEntries > vDBEntries;

    bool bTrigger = false;
    unsigned int ipFrom = 0 , ipTo = 0;
    
    string s = delName + "Del";
    ifstream in((findValue(s)).c_str());
     if ( !in ) {
        cout << s <<" File can NOT be opened ! \n";
        exit(1);
    }
    ifstream inDB ((findValue(dbIn)).c_str());
     if (!inDB ) {
        cout << dbIn <<" File can NOT be opened ! \n";
        exit(1);
    }
    ofstream outDB ((findValue(dbOut)).c_str() , ios::app);

    
    sEntry.clear();
    sStrArray.clear();
    vEntries.clear();
    vRanges.clear();
    vRangeIP.clear();
    vNets.clear();
    seEntries.clear();
    vDBEntries.clear();
    
    //    parse the Database to extract ipFrom, ipTo and country information. excerpt of the DB.
    //    "inetnum:      202.14.104.0 - 202.14.104.255"
    //    "country:      AU"
    while ( !(inDB.getline(cBuf,LINE_LENGTH).eof())  ) {
        sStr = cBuf;
        if ( sStr.empty() ) {
            bTrigger = true;
        }
        else if ( startWith ( sStr , "inetnum:") && (ipFrom == 0) && bTrigger ) {
            sEntry = split( sStr , ':' );
            if ( contain(sEntry[1],"-") ) {
                sIPFrom.clear();
                sIPTo.clear();
                sStrArray = split(sEntry[1],'-');
                sIPFrom = split ( sStrArray[0],'.' );
                sIPTo = split( sStrArray[1],'.' );

                ipFrom = convertToInt(sIPFrom);
                ipTo = convertToInt(sIPTo);
                bTrigger = false; 
            }
        }

        else if ( (ipFrom != 0) && startWith ( sStr , "country:" ) && (bTrigger == false) ) {
            sEntry.clear();
            sEntry = split( sStr , ':' );
            string str = trim ( sEntry[1]);            
            DBEntries entry;
            if ( (ipFrom != 0 && ipTo != UINT_MAX)  ) {
                entry.ipFrom = ipFrom;
                entry.ipTo = ipTo;
                entry.country[0] = toupper (str.c_str()[0]);
                entry.country[1] = toupper (str.c_str()[1]);
                
                // add entry to a set which will sort the entries based on [ipTo-ipFrom]
                seEntries.insert( entry );
            }
            ipFrom = 0;
        }
        else if ( startWith ( sStr , "inetnum:") && (ipFrom == 0) && (bTrigger== false) ) {
            cout<< "two ipFrom in one block" << endl;
        }
    }

    // add all elements of the set to a vector 
    set <DBEntries , comp>::iterator it;   
    for ( it = seEntries.begin(); it != seEntries.end(); it++ ) {
        vDBEntries.push_back(*it);
    }
    // clear the set
    seEntries.clear();

    // parse the delegation file to extract the ranges of the ips. excerpt of the deld. file
    // "3723493376-3724541951-JP"
    set < DBEntries , compare_entries > seStructEntries;
    
    while ( !(in.getline(cBuf,LINE_LENGTH).eof())  ) {
        sEntry.clear();
        sStr = cBuf;
        if( !sStr.empty() ) {
            stringstream sstream;
            sEntry = split( sStr , '-' );
            DBEntries sRange;
            sstream.clear();
            sstream << sEntry[0];
            sstream >> sRange.ipFrom;
            sstream.clear();
            sstream << sEntry[1];
            sstream >> sRange.ipTo;
            sRange.country[0] = sEntry[2][0];
            sRange.country[1] = sEntry[2][1];
            
            seStructEntries.insert( sRange );
        }
    }
    set <DBEntries , compare_entries>::iterator ite;   
    for ( ite = seStructEntries.begin(); ite != seStructEntries.end(); ite++ ) {
        vRanges.push_back(*ite);
    }
    
    unsigned int uRange = 0;
    ipFrom = 0;
    ipTo = 0 ;
    bool bTrig = true;

    // merge successive ranges if they are <= 16777216
    for ( unsigned int i = 0; i < vRanges.size()-1 ; i++ ) {
        if ( bTrig ) {
            ipFrom = vRanges[i].ipFrom;
            ipTo = vRanges[i].ipTo;
            uRange = ipTo - ipFrom;
            bTrig = false;
        }
        if ( uRange == 16777216 ) {
            DBEntries rIP;
            rIP.ipFrom = ipFrom;
            rIP.ipTo = ipTo;
            
            vRangeIP.push_back(rIP);
            bTrig = true;
        }
        else if ( (vRanges[i].ipTo + 1) == vRanges[i+1].ipFrom ) {
                if ( ((vRanges[i+1].ipTo - vRanges[i+1].ipFrom) + uRange) <= 16777216 ) {
                    uRange += vRanges[i+1].ipTo - vRanges[i+1].ipFrom;
                    ipTo = vRanges[i+1].ipTo;
                }
                else {
                    DBEntries rIP;
                    rIP.ipFrom = ipFrom;
                    rIP.ipTo = vRanges[i].ipTo;
                    vRangeIP.push_back(rIP);
                    bTrig = true;
                }
            
        }
        else {
            DBEntries rIP;
            rIP.ipFrom = ipFrom;
            rIP.ipTo = ipTo;
            vRangeIP.push_back(rIP);
            bTrig = true;
        }
    }

    unsigned int iRange[2];
    unsigned int ip = 0;
    unsigned int iMin = 0;
    int iIndex = 0;
    unsigned int iRangeValue = 0;
    bool bEnter = false;
    int iCounter = 0;
    unsigned int uDifference = 0;
    stringstream sstream;
    
    uDifference = vRangeIP.size();

    // this part will iterate over the ranges, then go through the DB looking 
    // for entries which are in this range, and assign the country 
    // of the entry to a part of the range. 

    for ( unsigned int ii = 0; ii < uDifference ; ii++ ) { // for-1
        iRange[0] = vRangeIP[ii].ipFrom;
        iRange[1] = vRangeIP[ii].ipTo;
        
        ip = 0;
        iMin = 0;
        iIndex = 0;
        bEnter = false;
        iCounter = 0;
        iRangeValue = iRange[1]-iRange[0] +1;

        // array of structures to keep the single ips of a range
        struct net * nets = new struct net [iRangeValue ] ; 

        // initialize the range of one entry in delegation file
        ip = iRange[0];
        for (unsigned int i = 0 ; i < iRangeValue ; i ++) {
            nets[i].ip = ip;
            nets[i].size = 0; 
            nets[i].country[0] = 'X';
            nets[i].country[1] = 'X';
            nets[i].bSetFlag = false;
            ip++;
        }
    
        ip = iRange[0] ;
        unsigned int ipF, ipT;
        unsigned int uDBSize = vDBEntries.size(); // size of the DB
        
        // check the database against the entry of the delegation file 
        for ( unsigned int i = 0 ; i < uDBSize ; i++  ) {
            if ( ((vDBEntries[i].ipFrom < iRange[0]) && 
                 (vDBEntries[i].ipTo < iRange[0])) || 
                 ( (vDBEntries[i].ipFrom > iRange[1]) && 
                 (vDBEntries[i].ipTo > iRange[1]) ) ) {
                continue;
            }
            else if ( (vDBEntries[i].ipFrom >= iRange[0]) && 
                      (vDBEntries[i].ipTo <= iRange[1]) ) {
                ipF = vDBEntries[i].ipFrom;
                ipT = vDBEntries[i].ipTo;
            }
            else if ( (vDBEntries[i].ipFrom <= iRange[0]) && 
                      (((vDBEntries[i].ipTo >= iRange[0]) && 
                      ((vDBEntries[i].ipTo <= iRange[1]) )) ) ) {
                ipF = iRange[0];
                ipT = vDBEntries[i].ipTo;
            }
            else if ( ((vDBEntries[i].ipFrom >= iRange[0]) && 
                      (vDBEntries[i].ipFrom <= iRange[1])) && 
                      (vDBEntries[i].ipTo > iRange[1]) ) {
                ipF = vDBEntries[i].ipFrom;
                ipT = iRange[1];
            }
            else if ( iRange[0] >= vDBEntries[i].ipFrom && 
                      iRange[1] <= vDBEntries[i].ipTo ) {
                ipF = iRange[0];
                ipT = iRange[1];
            }

            unsigned int uBeginIndex = ipF - iRange[0] ;
            unsigned int uEntryRange = ipT - iRange[0];
            
            // assign country to  every single ip
            for ( unsigned int k = uBeginIndex ; k <= uEntryRange ; k++ ) {
                unsigned int uDiff = vDBEntries[i].ipTo - vDBEntries[i].ipFrom;
                 
                if ( ( !nets[k].bSetFlag )  || ( uDiff < nets[k].size )) {
                    nets[k].country[0] = vDBEntries[i].country[0];
                    nets[k].country[1] = vDBEntries[i].country[1];
                    nets[k].size = uDiff;
                    nets[k].bSetFlag = true;
                }

            }
        }
                
        // merge single successor ips into one range
        vRanges.clear();
        
        for ( ite = seStructEntries.begin(); ite != seStructEntries.end(); ite++ ) {
            vRanges.push_back(*ite);
        }
        unsigned int value = 0;
        for ( unsigned int i = 0 ; i < iRangeValue ; i++ ) {
            value = i;
            
            for ( unsigned int j = i+1 ; 
                  ((j < iRangeValue) && 
                  ((nets[j].country[0] == nets[i].country[0]) && 
                  (nets[j].country[1] == nets[i].country[1]))) ; j++ ) {
                value = j;
            }
            
            if ( !((nets[value].country[0]== 'X') && 
                  (nets[value].country[1]== 'X')) ) {
                if (  nets[value].ip <  nets[i].ip) {
                    cout << "## Warning here " << nets[i].ip 
                         << "-"<<nets[value].ip << endl;
                    cout << "The Range is " << convertIP(ipF) 
                         << "-"<< convertIP(ipT) << endl;    
                }
                outDB << nets[i].ip << "-" << nets[value].ip << "-" 
                      << nets[value].country[0]<< nets[value].country[1]<< endl;
            }
            else {
                
                unsigned int uDelSize = vRanges.size(); // size of the Delegation file
                unsigned int ipF = nets[i].ip , ipT = nets[value].ip ;
                
                for ( unsigned int ij = 0 ; ij < uDelSize ; ij++  ) {
                    if ( (vRanges[ij].ipFrom <= ipF) && (vRanges[ij].ipTo >= ipT) ) {
                        outDB << nets[i].ip << "-" << nets[value].ip << "-" 
                              << vRanges[ij].country[0]<< vRanges[ij].country[1]<< endl;
                        break;
                    }    
                    else if ( ((vRanges[ij].ipFrom <= ipF) && 
                              (vRanges[ij].ipTo >= ipF)) && 
                              (vRanges[ij].ipTo < ipT)   ) {
                        outDB << nets[i].ip << "-" << vRanges[ij].ipTo << "-" 
                              << vRanges[ij].country[0]<< vRanges[ij].country[1]<< endl;
                    }
                    else if ( (vRanges[ij].ipFrom >= ipF ) && 
                              (vRanges[ij].ipTo <= ipT) ) {
                        outDB << vRanges[ij].ipFrom << "-" << vRanges[ij].ipTo << "-" 
                              << vRanges[ij].country[0]<< vRanges[ij].country[1]<< endl;
                                    
                    }
                    else if ( ((vRanges[ij].ipFrom >= ipF ) && 
                              (vRanges[ij].ipFrom <= ipT)) && 
                              (vRanges[ij].ipTo >= ipT) ) {
                        outDB << vRanges[ij].ipFrom << "-" << nets[value].ip << "-" 
                              << vRanges[ij].country[0]<< vRanges[ij].country[1]<< endl;
                        break;    
                    }
                }
            }
            i = value ;

        }
        
        vRanges.clear();
        delete [] nets;
        vNets.clear();
        sStr.clear();
        sEntry.clear();
    } // for-1     end of iteration over db
    

    in.close();
    inDB.close();
    outDB.close();
}


void delegParser( string delName, string delegOut  ) {
    char cBuf[LINE_LENGTH];
    
    string sStr;
    vector <string>  sEntry;
    vector <string>  sIPFrom , sIPTo;
    vector < DBRangeEntries > vRanges;
    
    ifstream in( (findValue(delName)).c_str());
    if (!in ) {
        cout << delName << " File can NOT be opened ! \n";
        exit(1);
    }
    ofstream outDB ((findValue(delegOut)).c_str(), ios::app);
    
    while ( !(in.getline(cBuf,LINE_LENGTH).eof())  ) {
        sEntry.clear();
        sIPFrom.clear();
        sStr = cBuf;

        if( startWith(sStr,delName) ) {
            sEntry = split( sStr , '|' );
            if ( ( sEntry[2] == "ipv4" ) && 
                 ( sEntry[1].length() == 2 ) && 
                 ( sEntry.size() == 7 ) ) {
                DBRangeEntries sRange;
                unsigned int temp;
                stringstream sstream;
                sstream.clear();
                sIPFrom = split ( sEntry[3] , '.' );
                sRange.ipFrom = convertToInt( sIPFrom );

                sstream << sEntry[4];
                sstream >> temp;
                sRange.ipTo = (sRange.ipFrom + (temp-1)) ;
                sRange.country[0] = sEntry[1][0];
                sRange.country[1] = sEntry[1][1]; 
                sRange.registry.assign(sEntry[0]);

                vRanges.push_back(sRange);
            }
        }
    }

    for ( int i = 0; i < (int)vRanges.size()-1 ; i++  ) {
        outDB << vRanges[i].ipFrom << "-" << vRanges[i].ipTo << "-" 
              << vRanges[i].country[0] << vRanges[i].country[1] << "-"
              << vRanges[i].registry << endl;
    }
    in.close();
    outDB.close();
    
}
