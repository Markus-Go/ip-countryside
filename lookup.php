<?php
/**
 * Copyright 2007 Deutsches Forschungszentrum fuer Kuenstliche Intelligenz 
 * or its licensors, as applicable.
 * Copyright 2008-2019 Markus Goldstein
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
 * Primary Repository: https://github.com/Markus-Go/ip-countryside/
 * Web Sites: madm.dfki.de, www.goldiges.de/ip-countryside
 *
*/

if (!isset($_GET["ip"] )) {
    $ip = $_SERVER["REMOTE_ADDR"];
    // if IPv6, replace by server IP
    if (!filter_var($ip, FILTER_VALIDATE_IP,FILTER_FLAG_IPV4)) {
        $ip = "37.221.195.97"; // $_SERVER["SERVER_ADDR"];
    }
} else {
    $ip = strip_tags(trim($_GET["ip"]));
}

$dlText = "The database is generated weekly. It can be dowloaded as a <a href=\"https://github.com/Markus-Go/ip-countryside/raw/downloads/ip2country.zip\">zip-file</a>.<br>";
$file = fopen("ip2country.db", "r") or die("Unable to open IP DB!");
if (file_exists("ip2country.zip")) {
    $last_modified = date("l, dS F Y, h:i a", filemtime("ip2country.zip"));
    $db_size = ceil(filesize("ip2country.zip")/1024);
    $dlText = "The database is generated weekly and was last created on " . $last_modified . " (CEST).<br> It can be dowloaded as a <a href=\"ip2country.zip\">zip-file</a> (" . $db_size . " kb).<br/>";
}

while(!feof($file)) {
    $line = fgets($file);
    if (substr_count($line," ") == 2) {
      list($start_ip[], $end_ip[], $country[]) = explode(" ",$line);
    }
}

$isValid = filter_var($ip, FILTER_VALIDATE_IP,FILTER_FLAG_IPV4);
if ($isValid) {
    list($a, $b, $c, $d) = explode(".",$ip);
    $ipvalue = (int)$a*256*256*256 + (int)$b*256*256 + (int)$c*256 + (int)$d;
} else {
    $comment = "You entered an invalid IP address!";
    fclose($file);    
}

if ($isValid) {
    $cn = $country[binSearch(0,count($start_ip),$ipvalue)];
    $cn_name = "Unknown";
    $flag = strtolower($cn); 
    $handle = fopen ("countries.txt","r") or die("Unable to open countries.txt!");

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
    list($a, $b, $c, $d) = explode(".",$ip);
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
Here we provide an on-line demo of our <a href="https://github.com/Markus-Go/ip-countryside/" target="_BLANK">ip-countryside</a> project.<br>
<?php print $dlText ?>
For more details please contact <a href="https://www.goldiges.de/contact" target="_BLANK">Markus Goldstein</a>.
</p>
<div align="center">
<form method="get" action="<?php echo $_SERVER['SCRIPT_NAME'];?>">
<font face="Arial" size="2"> IP Address: <input type="text" size="30" maxlength="15" name="ip" value="<?php print $ip; ?>"> </font><br />
<input type="submit" value="Find"> 
</form>
</div>
<br/><br/>


<table width="600" border="1" cellspacing="0" cellpadding="3" align="center">
<tr>
    <td> <font face="Arial" size="2">IP Address:</font> </td>
    <td> <font face="Arial" size="2"><b> <?php print($ip); ?></b></font> </td>
</tr>
<tr>
    <td><font face="Arial" size="2">Country Flag:</font></td>
    <td><font face="Arial" size="2"><b>
    <?php 
    if (!$isValid || empty($cn) ) {
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
    if (!$isValid ||empty($cn)) {
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
    if (!$isValid || empty($cn)) {
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
    if (!$isValid ) {
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
