<h1> VMware has ended active development of this project, this repository will no longer be updated.</h1><br># CAPE
## Cluster Automation for Pivotal Education
<img src="https://github.com/dbbaskette/cape/raw/gh-pages/images/cape.jpg" width="200"> 

* Automated cluster buildout for Google Compute. 
    * Support for Greenplum Database
    * Support for Pivotal HDB (Planned)
    
Requirements:
   * Tested against Python 2.7.12
   * Service Account:
   
      To set up Service Account authentication, you will need to download the corresponding private key file in the new JSON (preferred) format.
         
      Follow the instructions at https://developers.google.com/console/help/new/#serviceaccounts to create and download the private key.
         
      You will need the Service Account’s “Email Address” and the name of the key file for authentication.  These should be noted in the config.env file.  The keyfile should be placed in the ./configs directory.

   * SSH Username and Key:
   
      Create an SSH Key for the user you wish to use with GCE. (or use exiting one)  Go to the Metadata Page for your project.  Then select SSH-KEYS.   Hit Edit and Add Item.    Cut and Paste your Key in the box.  Click Save.

   * Requirements.txt file has the required External Python Libraries.

Use:

    python cape.py create --type gpdb --name <base name for cluster> --nodes <number of nodes>
    
