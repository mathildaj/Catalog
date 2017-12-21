# Project Description

This project uses python to generate a report based on analyzing the user logs. The logs are stored in a PostgreSQL database.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

1. Python 3 installed
2. VirtualBox and Vagrant installed (the version of these two software depends on your machine. I installed VirtualBox 5.1.30 and Vagrant 1.9.5)
3. Git bash or other command line tool installed

### Installing the application

1. Download or clone this VM onto your local machine: [VM for Log Analysis Project](http://github.com/udacity/fullstack-nanodegree-vm)
2. Download the database used for this project: [News](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip), unzip it, and place newsdata.sql into vagrant directory, which is shared with your virtual machine.
3. Download this project repository onto your local machine, and place report.py into the same directory where your newsdata.sql is.

## How to run the application

1. Start your Git Bash command tool.
2. cd into vagrant folder on your local machine, where you placed your VM image. Such as cd C:\MY_VM\vagrant
3. At command prompt, type vagrant up ($ vagrant up). This may take a long time to run for the first time. Be patient.
4. Once Git Bash is at the command prompt again, type vagrant ssh ($ vagrant ssh). This will let your log into your VM.
5. At the command prompt, type cd /vagrant to go to the relevant directory.
6. At the command prompt, type psql -d news -f newsdata.sql ($ psql -d news -f newsdata.sql) to load the database (You only need to load the data for the first time).
7. After step 6 is done, type \q to exit psql, and go back to the VM command prompt.
8. At the command prompt, type python report.py ($ python report.py). You will see the log analysis reports. The results should match report_output.txt file in this repository.


## Authors

* **Ying Xie**

## License

None

## Acknowledgements

* The VM image and database are downloaded from Udacity Full Stack Developer Program.

