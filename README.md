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

**Customization**

* Time-based thresholds for policies (e.g., `policyOneLimit`, `policyTwoWarningTime`) can be adjusted at the top of the script.  

**To-Do (For Development Purposes)**
* Consider adding command-line arguments to customize which policies should be included in the report.
* Write automated test cases.
* If email capabilities are required, implement sending functionality.

**Disclaimer**

This script interacts directly with a graph database. Use at your own discretion; take database backups before altering settings. 

**Contact**

* Feel free to reach out at [your email] for questions or feedback. 
 

**Explanation**

* **Clear Title:** Briefly states the purpose of the script.
* **Intro:**  Summarizes the script's core functionality and the three policies it enforces.
* **Features:** Concisely highlights key aspects.
* **Prerequisites:** Guides users on the necessary Python libraries and database access.
* **Setup:** Provides installation instructions and basic database configuration.
* **Usage:**  Gives the command format and explains necessary and optional arguments.
* **Customization:** Points out adjustable settings.
* **To-Do:** Suggests possible future improvements.
* **Disclaimer:** Emphasizes using the tool responsibly.
* **Contact:** Encourages communication.

**Let me know if you'd like any specific parts expanded on or other elements added to your README!** 
