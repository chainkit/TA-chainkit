# TA-chainkit

## Overview

This is a Chainkit app for Splunk Enterpirse. The app montiors and detects indexed logs on Splunk whether logs get tampered or not.

## Dependencies

* Splunk Enterprise 8.0+
* Splunk Add-on Builder 3.0.1
* Supported on Windows, Linux, MacOS, Solaris, FreeBSD, HP-UX, AIX

### 1) Install the Add-on Builder on Splunk Enterprise:
https://docs.splunk.com/Documentation/AddonBuilder/3.0.1/UserGuide/Installation

### 2) Download or clone TA-chainkit and make a .tar file and import it on the Add-on
  1. ```tar -czvf ${file_name}.tar.gz ${path}/TA-chainkit```
  2. Navigate to the Splunk Add-on Builder.
  3. Click `Import Project`.

### 3) Add a Splunk Account
  1. Go to Configuration in Chainkit App.
  2. Add a Splunk Account; This account must have permission for accessing data that you need to export.
  
<img width="1394" alt="Screen Shot 2020-06-02 at 4 02 41 PM" src="https://user-images.githubusercontent.com/47642039/83490570-3748a900-a4eb-11ea-94e3-bd750f6820d1.png">

### 4) Create an input
  * Interval: Set time `Interval` in seconds; this module will be run periodically with the given interval.
  * Index: Set `Index` that you would like to store a chainkit result.
  * Username/Password: This username/password must be generated by Chainkit.
  * Storage: There are three types of storage depending on your chainkit plan: `pencil`, `public`, `private`
  * API: Select either Register or Verify API.
  * Query:
    1. For Register, a query is used for exporting logs that you would like to register.
    2. For Verify, a query is simple: search index=`put the index you used for register API`
  * Earliest_time/Latest_time: These are a time bucket that retrives logs in the give time range.
  * Global Account: Select the account that you set above.
  
<img width="1354" alt="Screen Shot 2020-06-02 at 4 12 47 PM" src="https://user-images.githubusercontent.com/47642039/83502359-6adfff00-a4fc-11ea-81c5-15cf53b54dbc.png">


## Contact

This project was initiated by PencilDATA Inc.
<table>

<tr>
<td><em>Email</em></td>
<td>info@chainkit.com</td>
</tr>

</table>
  
