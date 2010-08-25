<?php
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
 * File: lookup.php
 * Purpose: PHP lookup demo client
 * Responsible: Markus Goldstein
 * Primary Repository: http://ip-countryside.googlecode.com/svn/trunk/
 * Web Sites: http://code.google.com/p/ip-countryside/, madm.dfki.de, www.dfki.de
 *
*/

if (!isset($_GET["ip"] ))
    $ip = $_SERVER["REMOTE_ADDR"];
else
    $ip = strip_tags(trim($_GET["ip"]));

$file = fopen("ip2country.db", "r") or die("Unable to open IP DB!");
$last_modified = date("l, dS F Y, h:i a", filemtime("ip2country.zip"));
$db_size = ceil(filesize("ip2country.zip")/1024);
$count = 0;
while(!feof($file)) {
    list($start_ip[$count], $end_ip[$count], $country[$count]) = split(" ",fgets($file));
    $count++;
}
    $error_code = 0;
    list($a, $b, $c, $d) = split("\.",$ip);

    if ((is_numeric($a) && is_numeric($b) && is_numeric($c) && is_numeric($d)) && 
          (($a >= 0 && $a <= 255) && ($b >= 0 && $b <= 255) && ($c >= 0 && $c <= 255) && ($d >= 0 && $d <=255))){
            $ipvalue = (int)$a*256*256*256 + (int)$b*256*256 + (int)$c*256 + (int)$d;
        }
    else {
        $comment = "You entered an invalid IP address!";
        fclose($file);    
        $error_code = 1;
    }


    if ($error_code == 0) {
        $cn = $country[binSearch(0,$count-1,$ipvalue)];
        $cn_name = "Unknown";
        $flag = strtolower($cn); 
        $handle = fopen ("countries.txt","r");

        while ( ($data = fgetcsv ($handle, 1000, ";")) !== FALSE ) {
            if(trim($data[1]) == trim($cn)) {
                $cn_name = ucfirst(strtolower($data[0]));
            }
        }

        fclose($file);
    }

function binSearch($start,$end,$search) {
    global $start_ip, $end_ip;
    $mid = $start+(int)(($end-$start)/2);
    if ($end < $start) {
        return -1;
    }
    if ($search < (int)$start_ip[$mid]) {
        return binSearch($start, $mid-1, $search);
    }
    else if ($search > (int)$end_ip[$mid]) {
        return binSearch($mid+1, $end, $search);
      }
    else return $mid;
}

function ip2int($ip) {
    list($a, $b, $c, $d) = split("\.",$ip);
    return (int)$a*256*256*256 + (int)$b*256*256 + (int)$c*256 + (int)$d;
}

?>

<html>
<head> 
<title>Country Lookup Demo</title>
</head>
<body>

<H1>Country Lookup Demo</H1>
<p>
Here we provide an on-line demo of our <a href="http://code.google.com/p/ip-countryside/" target="_BLANK">ip-countryside</a> project.<br>
The database is generated weekly and was last created on <?php print $last_modified; ?> (CEST).<br>
It can be dowloaded as a <a href="ip2country.zip">zip-file</a> (<?php echo $db_size; ?> kb).
< For more details please contact <a href="http://madm.dfki.de/goldstein/" target="_BLANK">Markus Goldstein</a>.
</p>
<div align="center">
<form method="get" action="<?php echo $PHP_SELF;?>">
<font face="Arial" size="2"> IP Address: <input type="text" size="30" maxlength="15" name="ip" value="<?php print $ip; ?>"> </font><br />
<input type="submit" value="Find"> 
</form>
</div>
</br></br>


<table width="600" border="1" cellspacing="0" cellpadding="3" align="center">
<tr>
    <td> <font face="Arial" size="2">IP Address:</font> </td>
    <td> <font face="Arial" size="2"><b> <?php print($ip); ?></b></font> </td>
</tr>
<tr>
    <td><font face="Arial" size="2">Country Flag:</font></td>
    <td><font face="Arial" size="2"><b>
    <?php 
    if ($error_code == 1 || empty($cn) ) {
        print ("-");
    }
    else
        print("<img src=\"flags/".$flag.".gif\">"); 
    ?> 
    </b></font></td>
</tr>
<tr>
    <td><font face="Arial" size="2">ISO Country Code: </font></td>
    <td><font face="Arial" size="2"><b>
    <?php
    if ($error_code == 1 ||empty($cn)) {
        print ("-");
    }
    else
        print($cn);
    ?>
    </b> </font></td>
</tr>
<tr>
    <td><font face="Arial" size="2">Country:</font> </td>
    <td><font face="Arial" size="2"><b>
    <?php 
    if ($error_code == 1 || empty($cn)) {
        print ("-");
    } 
    else 
        print($cn_name); 
    ?>
    </b> </font></td>
</tr>
<tr>
    <td><font face="Arial" size="2">Comment: </font> </td>
    <td><font face="Arial" size="2"><b>
    <?php 
    if ($error_code == 1) {
        print ($comment);
    }
    else if (empty($cn)) 
        print("Not Assigned");
    else print("-");
    ?>
    </b> </font></td>
</tr>
</table>
</body>
</html>
