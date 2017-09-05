# Restaurant Menu Project

Utilizes Flask and SQL Alchemy to generate a database for Restaurants, Menu Items, and website Users.

Users can log in via Facebook or Google Plus. In order to add a restaurant, the user must be logged in. Restaurants and their menus can only be edited by the user who created them, or the first user created on the database after the dummy user (user ID 2). User ID 2 acts as a Moderator to protect the application quickly and without the need to alter the code. Alternatively, the templates can be modified to grant this ability to a user with a specific email.

Check out the live demo [here](https://menupoly.herokuapp.com)!

## Requirements
* Python 2
* Flask 0.12.2
* SQL Alchemy 1.1.12
* OAuth2Client 4.1.2
* Requests 2.18.2

Preferred:
* [Udacity's Full Stack VM](https://github.com/udacity/fullstack-nanodegree-vm)
* [Vagrant](https://www.vagrantup.com/downloads.html)
* [Oracle VirtualBox VM](https://www.virtualbox.org/wiki/Downloads)

## Installation
Using Git Bash:

`$ git clone https://github.com/tiffanystallings/project-restaurant-menu.git`

From a ZIP:
1. Visit the project's github [here](https://github.com/tiffanystallings/project-restaurant-menu)
2. Click the **Clone or Download** dropdown box and select  
**Download ZIP**.
3. Open the ZIP and click **Extract All**. Select your preferred  folder and hit **Extract**.

## Setting up the Virtual Environment
To re-create the environment in which this was built and run it locally, you will need Udacity's Full Stack Nanodegree VM. The VM is built with all of the requirements for this project, making usage a lot more simple.

To install the VM, use Git Bash.

`$ git clone https://github.com/udacity/fullstack-nanodegree-vm.git`

With Vagrant and Oracle VirtualBox VM installed (see the "Preferred" section of Requirements above), use Git Bash to navigate to the "vagrant" folder inside the fullstack-nanodegree-vm repository.

`$ cd fullstack-nanodegree-vm/vagrant`

Clone the project-restaurant-menu repository here, but do not navigate to it.

`$ git clone https://github.com/tiffanystallings/project-restaurant-menu.git`

If Vagrant and VirtualBox are properly installed, and if your machine is configured for virtualization, you should be able to initialize a Vagrant virtual machine by entering:

`$ vagrant up`

It is normal for the first "vagrant up" to take a few minutes, as it is handling a number of installations. Once it has completed, you will be regain access of your command line. Enter:

`$ vagrant ssh`

If Vagrant was able to set up the virtual machine smoothly, you will be logged in to a virtual Ubuntu machine and have access to its command line. Now, navigate to the restaurant menu directory.

`$ cd /vagrant/project-restaurant-menu`

## Setting up the Database
From either your Vagrant virtual machine or a machine configured with the above Requirements, and while in the project directory run:

`$ python database_setup.py`

This will initialize the database and create a restaurantmenuwithusers.db file in the root folder of the repository. To populate the database with fake restaurants, menus, and a dummy user run:

`$ python database_create.py`

This is optional, but highly recommended. The program is currently configured for the second user (first after the dummy user) to have moderator-like abilities. Unwanted restaurants can be easily removed from the database via the web page, if need be. It will also allow you to see what the website looks like when restaurants have been added.

Once the database is set up, the server can be run.

## Usage
After the database has been set up, you are ready to start the server. While still in the project directory, run:

`$ python flaskserver.py`

Open your preferred browser and go to [http://localhost:5000](http://localhost:5000). This should take you to the "Menupoly" landing page.

Note: Sign in through Facebook and Google should work, but they depend on using the client secrets assigned to this program. Logging in will only work on software originating from either the live demo, or a localhost IP. It is highly recommended that you generate your own client secrets and implement them, as I reserve the right to strip access to mine should I find them being used nefariously.

Assuming you ran database_create.py in the setup, upon logging in for the first time you will be given the ability to edit and delete any restaurant or menu item. If you want to see what the website looks like as another user, you will need to sign in with a Google or Facebook account using an alternate e-mail address.

Once signed in you will have the ability to create new restaurants, edit the name of those restaurants, delete those restaurants, and do the same for menu items on those restaurants' pages. Users who are not on the Mod account (user ID 2) will only be able to edit and delete their own content, not the content of other users.

## Contributions
This project was built as part of Udacity's Full Stack Web Developer Nanodegree. It would be in violation of the honor code for me to accept any direct contributions to the code.

However, if you have any advice or suggestions on how I might improve the code, please feel free to take out an Issue on the project's [github](https://github.com/tiffanystallings/project-restaurant-menu).
