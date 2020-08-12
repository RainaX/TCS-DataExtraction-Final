# TCS-DataExtraction

Note: The product was originally built on an AWS EC2 instance of Ubuntu Deep Learning AMI.

## Installation
---
## Requirements
- Linux
- Python 3.6+
- Java 9+
- PyTorch 1.3+
- Cuda 9.2+
- GCC 5+

## Install mmdetection
a. Activate a conda virtual environment with PyTorch and torchvision installed. If you are using Deep Learning AMI, just use the following command:
    
    source activate pytorch_p36

b. Clone the mmdetection repository.
    
    git clone https://github.com/open-mmlab/mmdetection.git
    
c. Install mmcv.

    pip install mmcv-full==1.0.5
    
d. Enter mmdetection directory to install build requirements and then install mmdetection.

    cd mmdetection
    pip install -r requirements.txt
    python setup.py install
    python setup.py develop
    
    
## Install Java and Tomcat

You can follow instructions in this [video](https://www.youtube.com/watch?reload=9&v=_d-c9uGcUrU) on how to deploy a Java web application on AWS EC2 instance using Tomcat, or read the instructions below.

a. Install java following the [official guide](https://java.com/en/download/help/linux_x64_install.xml).

For Deep Learning AMI, Java has already been installed.

b. Download the Tomcat Binary from the [official site](https://tomcat.apache.org/download-80.cgi). For example, you can download the core tar.gz file and untar it.

    wget https://downloads.apache.org/tomcat/tomcat-8/v8.5.57/bin/apache-tomcat-8.5.57.tar.gz
    tar xvfz apache-tomcat-8.5.57.tar.gz
    
c. If you are using Deep Learning AMI, you need to remove restrictions set by both Tomcat and AWS so that you can have access to the server on a remote machine.

First modify the file `apache-tomcat-8.5.57/webapps/manager/META-INF/context.xml`. You can see a `Valve` tag within the `Context` tag. It might look like this:
    
    <Valve className="org.apache.catalina.valves.RemoteAddrValve"
         allow="127\.\d+\.\d+\.\d+|::1|0:0:0:0:0:0:0:1" />
        
Command out this line so that the `Context` tag becomes

    <Context antiResourceLocking="false" privileged="true" >
        <!-- <Valve className="org.apache.catalina.valves.RemoteAddrValve"
         allow="127\.\d+\.\d+\.\d+|::1|0:0:0:0:0:0:0:1" /> -->
        <Manager sessionAttributeValueClassNameFilter="java\.lang\.(?:Boolean|Integer|Long|Number|String)|org\.apache\.catalina\.filters\.CsrfPreventionFilter\$LruCache(?:\$1)?|java\.util\.(?:Linked)?HashMap"/>
    </Context>

Then go to your EC2 dashboard and click on the `Security Group` link on the far right of instance, and add a new inbound rule to allow for access to port 8080. Specifically, click `Inbound rules` card tag, then click `Edit inbound rules` -> `Add rules`. Select Type `Custom TCP`, Port range `8080`, and Source `Custom`, `0.0.0.0/0`. Then click on `Save rules`.

d. Set up username and password as app manager on Tomcat. Modify file `apache-tomcat-8.5.57/conf/tomcat-users.xml` and append user configuration to the file. For example, you can add the following line right before the closing tag `</tomcat-users>`.

    <role rolename="manager-gui"/>
      <user username="admin" password="admin" roles="manager-gui"/>
      

## Install the table extraction web application
     
a. Clone this github repository. We saved the folder at path `/home/ubuntu/`. You need to modify all python files to replace this path with your own if you saved the folder in another directory.

b. Go to your Apache Tomcat directory and then go to `bin/` folder. Run the following command in your shell to start the Tomcat server:

    ./startup.sh
    
c. Type in the public DNS of your instance in your browser with port 8080, i.e., `ec2-xxxxxxxx.amazonaws.com:8080`, and you can see the front page of Tomcat server. Click on `Manager App` button and enter the username and password you have just set up. In the `Deploy` section, enter the absolute path to `.war` file in this repository in `Contect Path (required)`, then click on `Deploy` button.

d. After deploying the application, you can find the corresponding url of this app in the dashboard. You can then enter `ec2-xxxxxxxx.amazonaws.com:8080/AppName` to visit the webpage and use our product.

e. After you have finished work on the product, go to your Apache Tomcat directory and then go to `bin/` folder. Run `./shutdown.sh` to stop the Tomcat server.
