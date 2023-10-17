# Time Management App
A Computer Science 3 project to help students manage their time properly. A massive feat for this generation.

Install all libraries
```python
pip install -r requirements.txt
```

Eshan's time on this project:\
[![wakatime](https://wakatime.com/badge/user/d2cf396a-1b98-4795-9559-b880684c63b7/project/018b25b5-8d65-4d6e-9fdd-8758cee7e4a9.svg)](https://wakatime.com/badge/user/d2cf396a-1b98-4795-9559-b880684c63b7/project/018b25b5-8d65-4d6e-9fdd-8758cee7e4a9?style=flat-square)

## Roles

<div style="display: flex; justify-content: space-between; margin: 20px;">

  <!-- Table 1: Lead Developers -->
  <table>
    <thead>
      <tr>
        <th>Names</th>
        <th>Position</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Elijah</td>
        <td>Overall Leader</td>
      </tr>
      <tr>
        <td>Eshan</td>
        <td>Lead Developer</td>
      </tr>
      <tr>
        <td>Abhiram</td>
        <td>Lead Developer</td>
      </tr>
      <tr>
        <td>Kapilesh</td>
        <td>Lead Developer</td>
      </tr>
      <tr>
        <td>Ayush</td>
        <td>Lead HTML Developer</td>
      </tr>
    </tbody>
  </table>

  <!-- Table 2: HTML Developers -->
  <table>
    <thead>
      <tr>
        <th>Names</th>
        <th>Position</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Naythan</td>
        <td>HTML Developer</td>
      </tr>
      <tr>
        <td>Manas</td>
        <td>HTML Developer</td>
      </tr>
      <tr>
        <td>Suchay</td>
        <td>HTML Developer</td>
      </tr>
      <tr>
        <td>Sithranjan</td>
        <td>HTML Developer</td>
      </tr>
    </tbody>
  </table>

  <!-- Table 3: Designers -->
  <table>
    <thead>
      <tr>
        <th>Names</th>
        <th>Position</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Mansha</td>
        <td>Head Design</td>
      </tr>
      <tr>
        <td>Rishitha</td>
        <td>Design</td>
      </tr>
      <tr>
        <td>Kaveh</td>
        <td>Design</td>
      </tr>
      <tr>
        <td>Rajeswari</td>
        <td>Design</td>
      </tr>
      <tr>
        <td>Rithwik</td>
        <td>Design</td>
      </tr>
      <tr>
        <td>Revanth</td>
        <td>Design</td>
      </tr>
      <tr>
        <td>Jordan</td>
        <td>Design</td>
      </tr>
      <tr>
        <td>Kevin</td>
        <td>Design</td>
      </tr>
    </tbody>
  </table>
</div>



## Google Calendar API Setup

***I will send you the credentials.json file that this process produces. This is to create your own file. The file is not here for security reasons***

### **Create a Google Cloud Project ([Link](https://developers.google.com/workspace/guides/create-project))**


### **Enable the API**

Before using Google APIs, you need to turn them on in a Google Cloud project. You can turn on one or more APIs in a single Google Cloud project.
In the Google Cloud console, [enable the Google Calendar API](https://console.cloud.google.com/flows/enableapi?apiid=calendar-json.googleapis.com). 


### **[Configure the OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)**
If you're using a new Google Cloud project to complete this quickstart, configure the OAuth consent screen and add yourself as a test user. If you've already completed this step for your Cloud project, skip to the next section.

In the Google Cloud console, go to Menu menu > APIs & Services > OAuth consent screen.
Go to OAuth consent screen

Select the user type for your app, then click Create.
Complete the app registration form, then click Save and Continue.
For now, you can skip adding scopes and click Save and Continue. In the future, when you create an app for use outside of your Google Workspace organization, you must add and verify the authorization scopes that your app requires.

If you selected External for user type, add test users:
Under Test users, click Add users.
Enter your email address and any other authorized test users, then click Save and Continue.
Review your app registration summary. To make changes, click Edit. If the app registration looks OK, click Back to Dashboard.

### **Authorize [credentials](https://console.cloud.google.com/apis/credentials) for a desktop application**
To authenticate as an end user and access user data in your app, you need to create one or more OAuth 2.0 Client IDs. A client ID is used to identify a single app to Google's OAuth servers. If your app runs on multiple platforms, you must create a separate client ID for each platform.
In the Google Cloud console, go to Menu menu > APIs & Services > Credentials.
Go to Credentials

Click Create Credentials > OAuth client ID.
Click Application type > Desktop app.
In the Name field, type a name for the credential. This name is only shown in the Google Cloud console.
Click Create. The OAuth client created screen appears, showing your new Client ID and Client secret.
Click OK. The newly created credential appears under OAuth 2.0 Client IDs.
Save the downloaded JSON file as credentials.json, and move the file to your working directory.

### **Install the Google client library**
```python
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
