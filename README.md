# policyWarningScript
Policy Warning Script

# Graph Policy Warning Report Script

This Python script automates the generation of policy warning reports for a graph database system. It is designed to monitor and enforce policies regarding:

* **Policy 1:** Limiting the number of versions (cell/mode combinations) per user.
* **Policy 2:** Identifying and managing long-inactive servers.
* **Policy 3:** Identifying and managing unreferenced servers.

**Features**

* Connects to a MySQL database for data retrieval.
* Implements customizable time-based thresholds for warnings and errors.
* Generates reports designed to either be printed to the console (stdout) or optionally sent via email.

**Prerequisites**

* Python 3 
* The following Python libraries:
    * argparse
    * collections
    * datetime
    * pandas
    * pandasql
    * pymysql 
    * subprocess
* Access to the target graph database with appropriate credentials.

**Setup**

1. **Install Dependencies:**
   ```bash
   pip install argparse collections datetime pandas pandasql pymysql subprocess
   
2. **Database Configuration:**
   * Create a file named `/.../imyers/psswd/db` (adjust accordingly) and insert your database password there.
   * Update the `db` variable in the script if your graph database has a different name.

**Usage**

bash
python policy_warning_report.py -email your_email@domain.com [-m | -s] 


* **Required arguments:**
   * `-email your_email@domain.com`: Specifies the email address to receive the report.
* **Optional arguments:**
   * `-m` : Send the report to your email.
   * `-s` : Print the report to the console (default behavior).


