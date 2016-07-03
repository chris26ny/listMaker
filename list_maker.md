# Catalog project 
## listMaker
##### Udacity Full-Stack Nanodegree program
##### Chris Wieland
##### 2016

-------------------------
### Contents:
-------------------------
* listMaker.py
* database_setup2.py
* login.html
* all_lists.html
* view_list.html
* edit_list.html
* delete_list.html
* new_item.html
* edit_item.html
* delete_item.html
* list_maker.css
* client_secrets.json

------------------------
### App description:
------------------------

A simple way to create a list for any purpose (to-do list, grocery list, itinerary, recipe ingredients, note-taking, etc..)

------------------------
### How to setup and run app:
------------------------

##### Setup
* In order to run this app you will need to have Python, SQLalchemy and Flask installed locally or running on a virtual machine.  To setup the VM for this project:
	* Install [VirtualBox](http://Virtualbox.org)
	* Install [Vagrant](htttp://vagrantup.com)
	* Use git to fork, then clone the VM config
	* From the terminal, run:
        ```
        git clone http://github.com/<username>/fullstack-nanodegree-vm fullstack
        ```
    * Using the terminal, change directory to fullstack/vagrant (cd fullstack/vagrant), then type vagrant up to launch your virtual machine.
Once it is up and running, type vagrant ssh to log into it. This will log your terminal in to the virtual machine, and you'll get a Linux shell prompt. When you want to log out, type exit at the shell prompt.  To turn the virtual machine off (without deleting anything), type vagrant halt. If you do this, you'll need to run vagrant up again before you can log into it. Be sure to change to the /vagrant directory by typing cd /vagrant in order to share files between your home machine and the VM.

* Download and save all app contents to a new folder within the fullstack/vagant directory.  

* Change directory to the newly created folder containg the app.

* From the terminal, run the web-app by typing:
    ```
    python listMaker.py
    ```
* Visit http://localhost:5000 to view the app  

##### Creating a new list and adding items

* Login using a google account
* Click on 'create list' button to bring up the new list form.
* Enter list name and description. Submit form. 
* Click on newly created list to bring up the items page
* Click 'new item' to add a new item to the list

#### Possible features for next update

* More item options including photo, description and date/time
* Option to give lists a category label and filter home page by different categories. 
* Option to add numbered items
* Sign-in with Facebook or create account with email
* Ability to edit, delete or cross-out items without leaving page
* Ability to edit and delete lists without leaving page
* Flash messages after successfully creating or updating list/items. 









