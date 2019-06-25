# Catalog Item

This project is an application that provides a list of sport items within a number of different categories while provides a user with registration and authentication system. Authorized user could create, update and delete their own items in this web application.

## Prerequisites

Things you need to install before running the script
```
python2
```
```
Vagrant
```
```
VirtualBox
```
You'll use a virtual machine (VM) to run a web server and a web app that uses it. The VM is a Linux system that runs on top of your own machine. 

### VirtualBox

VirtualBox is the software that actually runs the VM. [You can download it from virtualbox.org, here.](https://www.virtualbox.org/wiki/Downloads)  Install the *platform package* for your operating system.  You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it.

### Vagrant

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem.  [You can download it from vagrantup.com.](https://www.vagrantup.com/downloads) Install the version for your operating system.

## Design
The main file in this project is ```application.py```. This python script implements the functionalities of the Flask application that could view, post, edit and delete users' own items.


## Running the tests

### Run the virtual machine

Using the terminal, change directory to project directory (**cd project2_YangLiu**), then type **vagrant up** to launch your virtual machine.

### Log into the virtual machine

Once it is up and running, type **vagrant ssh**. This will log your terminal into the virtual machine, and you'll get a Linux shell prompt. 

Now that you have Vagrant up and running type **vagrant ssh** to log into your VM.  change to the /vagrant directory by typing **cd /vagrant**. This will take you to the shared folder between your virtual machine and host machine.

Type **ls** to ensure that you are inside the directory that contains application.py, database_setup.py, lotsofcatalogs.py, client_secrets.json and two directories named 'templates' and 'static'

### Create a sample database

Now type **python database_setup.py** to initialize the database.

Type **python lotsofcatalogs.py** to populate the database with sport catergories and items. (Optional)

### Running the Restaurant Menu App

Here is the final step! 

Type **python project.py** to run the Flask web server. In your browser visit **http://localhost:8000** to view the catalog item app.  You should be able to view, add, edit, and delete menu items and restaurants.


## Author

* **Yang Liu** 


## Notificatoin
Parts of the above instructions are copied from Udacity - Full Stack Web Developer Nanodegree Lesson.
