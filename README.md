## Uncertainty Managed Access to Microstructures Interface Project
To run replicate this project we open commandline terminal and type following
```
$git clone https://github.com/push44/UMAMI.git
$cd UMAMI
$pip install -r requirements.txt
$mkdir input
$cd src
$touch config.py
```
At this point we have to put url address, username, and password in the config.py file.<br>
For example,
```
URL = "www.google.com"
USERNAME = "username"
PASSWORD = "password"
```
Now we are all set to run get.py file by following command in the terminal
```
$python get.py
```
This script extracts data from the url address and stores it into the input folder.<br>
Now we are ready run run app.py. Again open the terminal and type following
```
$python app.py
```
You will result in something like this
![start_server](https://user-images.githubusercontent.com/61958160/127756262-4c1b4174-dfe2-4030-bd48-954439672927.png)
<br>
Once server is running click on the http address and browser will open up the app.<br>
By default two options are selected to present deault scatter plot.
![default](https://user-images.githubusercontent.com/61958160/127756255-0f1fcb83-eca5-4d07-880b-4159ac4c0f6c.png)
<br>
You can choose options from dropdown menu similar to shown in following image.
![selection](https://user-images.githubusercontent.com/61958160/127756257-7457d5c2-f096-4cb1-9598-62a04952329d.png)
Default scatter plot automatically gets updated by the user selections.
![new_plot](https://user-images.githubusercontent.com/61958160/127756260-6c347170-392f-43d7-bcd1-ab834fbe4723.png)
