<h1 align="center">
  <br>
  <a href="https://phoenixnap.com/bare-metal-cloud"><img src="https://user-images.githubusercontent.com/81640346/127175085-9cf4faed-852d-46e3-a25a-1250e953c79e.png" alt="phoenixnap Bare Metal Cloud" width="300"></a>
  <br>
  Apigee Automation 
  <br>
</h1>

<p align="center">
The purpose of this repo is to hold automation code related to Apigee.
</p>
<p align="center">
  <a href="https://phoenixnap.com">phoenixNAP Official Website</a> •
  <a href="https://developers.phoenixnap.com/">BMC Developers Portal</a> •
  <a href="http://phoenixnap.com/kb">Knowledge Base</a> •
  <a href="https://developers.phoenixnap.com/support">Support</a>
</p>


## upload_spec.py

Currently there is no API provided from Apigee which lets you upload an OpenAPI spec. Therefore **upload_spec.py** was created to leverage ajax calls done in the UI when uploading a spec from there.

This script requires the following arguments to run successfully:

- **name** - The name of the spec that will be uploaded to Apigee. If this is not unique, the spec with the same name in Apigee will be updated.

- **file** - The path of the spec on your machine.

- **org** - The organization name in Apigee. **https://apigee.com/organizations/johnd-eval/proxies** has organization name **johnd-eval**.

- **username** - The username of the Apigee user that the script uses to fetch an access token.  This access token is used in any other subsequent rest calls.  The access_token will expire every 12 hours.  Usually a dedicated automation user is used here.

- **password** - The password for the above username.

- **refresh_token** - A refresh token can be used instead of the above username and password.  Note that the refresh tokens have an expiry of 1 month.

## upload_api_product.py

This script leverages the Apigee Management API to create or update an API Product. The following arguments are required for the script to run successfully:

**file** - JSON file representing the API Product to be created. An example of how to create it can be found in the [Create API Product](https://apidocs.apigee.com/management/apis/post/organizations/%7Borg_name%7D/apiproducts) or [Update API Product](https://apidocs.apigee.com/management/apis/put/organizations/%7Borg_name%7D/apiproducts/%7Bapiproduct_name%7D) section of the Apigee Management API documentation. Name is always mandatory is the JSON file since it is used to check if the API Product exists or not. If the API product exists, it is updated with then new JSON file.

**org** - Same as in **upload_spec.py**.

**username** - Same as in **upload_spec.py**.

**password** - Same as in **upload_spec.py**.

**refresh_token** - Same as in **upload_spec.py**.

## upload_portal_documentation.py

As there is no API to create or update Portal Documentation on Apigee, this script leverages their the calls used in the Apigee UI. It takes care of creating or updating the Apigee Portal Documentation.

**file** - JSON file representing the API Portal Documentation to be created. An example of the JSON is:

```json
{
  "title": "Test Portal",  -- The name of the API Portal Documentation.
  "edgeAPIProductName": "test-product", -- The name of the API product to base the documentation on.
  "visibility": true, -- Whether to show this documentation in the portal or not.
  "anonAllowed": true, -- Allows any user to access the portal documentation without logging in.
  "requireCallbackUrl": true, -- Forces the a callback URL to be set when creating applications for this API.
  "orgname": "johnd-eval", -- The name of the organization hosting this portal documentation
  "specContent": 12345, -- The Apigee ID of the spec.
  "specId": "test", -- The name of the spec which this portal API is based on.
}
```

`orgname` and `specId` are provided as parameters so they should not be part of the JSON file, otherwise they will be overwritten. `specContent` is retrieved from the `specId` provided, since we are working on the premise that a spec name will always be unique.

**portal** - Full name of the portal where we want to create the documentation. e.g. If a portal is accessed through `https://johnd-eval-test.apigee.io`, the full name of the portal is `johnd-eval-test`.

**org** - Same as in **upload_spec.py**.

**username** - Same as in **upload_spec.py**.

**password** - Same as in **upload_spec.py**.

**refresh_token** - Same as in **upload_spec.py**.

## upload_theme.py

This python script leverages Apigee internal APIs to maintain an apigee portal look and feel, by modifiying logos, stylesheets etc.  This script uses a custom configuration file described below, to reference different theme resoures. 

**file** - path to JSON file with configurations to the theme:

```json
{
  "overridesFile": "test/ph-dev/portal/theme/style/variables.scss", --path to an scss file containing an overrides to default variables.   
  "customScssFile": "test/ph-dev/portal/theme/style/custom.scss", --path to an scss file containing style overrides.
  "logoFile": "test/ph-dev/portal/theme/images/logo.png", --path to the logo to be used for the page
  "mobileLogoFile": "test/ph-dev/portal/theme/images/logo.png", --path to the logo to be used for the mobile page
  "faviconFile": "test/ph-dev/portal/theme/images/favicon.png" --path to the fav icon
}
```

:book: [Learn more about default variables here](https://docs.apigee.com/api-platform/publish/portal/api-portal-themes#override-variables)

:book: [Learn more about custom css here]( https://docs.apigee.com/api-platform/publish/portal/api-portal-themes#style-elements)

**portal** - Full name of the portal where to upload the theme. e.g. If a portal is accessed through `https://johnd-eval-test.apigee.io`, the name of the portal is `test`.

**org** - Same as in **upload_spec.py**.

**username** - Same as in **upload_spec.py**.

**password** - Same as in **upload_spec.py**.

**refresh_token** - Same as in **upload_spec.py**.

## upload_assets.py

This python script leverages Apigee internal APIs to synch all the local assets to the portal's assets.

**folder** - path to a folder which contains all the assets.  Note that only assets found in the root level of folder will be synched.  Any child folders and their contents will be ignored.

**portal** - Same as in **upload_theme.py**.

**org** - Same as in **upload_spec.py**.

**username** - Same as in **upload_spec.py**.

**password** - Same as in **upload_spec.py**.

**refresh_token** - Same as in **upload_spec.py**.

**clean** - USE WITH CAUTION, as this switch will delete any file that is not present in the assets folder.

## upload_single_asset.py

This python script leverages Apigee internal APIs to upload a file to the portal.

**file** - the location of the file to upload to the portal.

**portal** - Same as in **upload_theme.py**.

**org** - Same as in **upload_spec.py**.

**username** - Same as in **upload_spec.py**.

**password** - Same as in **upload_spec.py**.

**refresh_token** - Same as in **upload_spec.py**.

## upload_pages.py

This python script leverages Apigee internal APIs to synch all the local html/md pages to the portal.  It also takes care of reconstructing the menu structure on the portal.  Note that each time this script is run, all menu items are deleted and re created.

**folder** - path to a folder which contains all the pages.  Note:
  * only .html, .htm, .md files found in the root level of folder will be synched.  
  * Any child folders and their contents will be ignored.  
  * *It is very important that the home page is called index.html, otherwise the portal won't work*.
  * It is suggested that kebab-case is used as a naming convention for the filenames.  The file name will be used to derive the name page.  e.g. knowledge-base.html will create a page with a name *Knowledge Base*

**menu** - path to a JSON file specification which will define the menu structure.  Note that the structure is split into a header menu and a footer menu.  Also note that a root menu items can have a number of child menu items.  Finally a menu item can either point to an internal portal page (simply by defining the name of the file - without extension), or to an external link.  The following is an example of the json file:

```json
{
  "header": [             --header, contains a list of menu items
    {
      "name":"Home",      --Name for the menu item
      "page": "index",    --if menu-item points to an internal page, the name (without extension) of the page
      "url": null,        --if menu-item points to an external URL, fill this url
      "sub_menu": []      --a list of sub menu items.  Leave empty if there is none
    },
    {
      "name":"Knowledge Base",          --This is an example of a menu with sub menu items.  
      "page": null,                     --Note that both page and url can be left empty
      "url": null,
      "sub_menu": [
        {                               --This is an example of 2 child menus.  Note that they don't have further sub menus
          "name":"Connect using REST",
          "page": "curl",
          "url": null
        },
        {
          "name":"Connect using CLI",
          "page": "cli",
          "url": null
        }
      ]
    }
  ],
  "footer": [         --footer, similar to header, contains a list of menu items
    {
      "name":"Terms and Conditions",
      "page": null,
      "url": "http://fakewebsite.com/terms-and-conditions.html",
      "sub_menu": []
    }
  ]
}
```

**portal** - Same as in **upload_theme.py**.

**org** - Same as in **upload_spec.py**.

**username** - Same as in **upload_spec.py**.

**password** - Same as in **upload_spec.py**.

**refresh_token** - Same as in **upload_spec.py**.

## upload_portal.py

This python script leverages Apigee internal APIs to create a portal if it doesn't exist, or update its settings.

**file** - path to a json file which contains the configuration of the portal.
```json
{
  "name": "temp1",                                            -- name of portal
  "description": "Added automatically by automation tool 2",  -- description of portal
  "analyticsScript": "",                                      -- analytrics script to be added
  "analyticsTrackingId": "",                                  -- google analytics tracking id
  "customDomain": "",                                         -- not implemented yet
  "idpEnabled": "false"                                       -- not implemented yet
}
```
**portal** - If specified, this will be the name of the created portal and will override the name key value pair in the JSON.

**org** - Same as in **upload_spec.py**.

**username** - Same as in **upload_spec.py**.

**password** - Same as in **upload_spec.py**.

**refresh_token** - Same as in **upload_spec.py**.

## generate_report.py

This script reads a JSON file containing a payload as shown in the [Create an asynchronous analytics query documentation](https://apidocs.apigee.com/management/apis/post/organizations/%7Borg_name%7D/environments/%7Benv_name%7D/queries). A report is generated by Apigee based on that file and is then saved in the specified location if given. If no location is given, the query result is saved in the current directory. The file is saved `csv.gz` format.

**org** - Same as in **upload_spec.py**.

**env** - The environment we want to base the report on. Examples of environments are `prod` and `test`.

**file** - The JSON file containing the details of how Apigee should generate the report. Refer to [Create an asynchronous analytics query documentation](https://apidocs.apigee.com/management/apis/post/organizations/%7Borg_name%7D/environments/%7Benv_name%7D/queries) for what can be included.

**output** - The location of where the `.csv.gz` query result output file should be saved.

**startdate** - The start date of the report. This needs to be specified as an argument in the python script instead of part of the JSON payload.

**enddate** - The end date of the report. This needs to be specified as an argument in the python script instead of part of the JSON payload.

**groupbytimeunit** - Time unit used to group the result set. Valid values include: second, minute, hour, day, week, or month

**username** - Same as in **upload_spec.py**.

**password** - Same as in **upload_spec.py**.

**refresh_token** - Same as in **upload_spec.py**.

## Example Scripts

```bash
python3 automation/upload_portal.py --file ~/dev-env/portal/portal.json --org testOrg --username automationuser --password xxxx
python3 automation/upload_theme.py --file ~/dev-env/portal/theme/theme_configuration.json --portal test --org testOrg --username automationuser --password xxx
python3 automation/upload_assets.py -f ~/dev-env/portal/assets -p test -o testOrg -u automationuser -pwd xxx
python3 automation/upload_pages.py -f ~/dev-env/portal/pages -m ~/test/ph-dev/portal/pages/menu_items.json -p test -o testOrg -u automationuser -pwd xxx
```

### Contact phoenixNAP

Get in touch with us if you have questions or need help with Bare Metal Cloud or our other infrastructure solutions.

<p align="left">
  <a href="https://twitter.com/phoenixNAP">Twitter</a> •
  <a href="https://www.facebook.com/phoenixnap">Facebook</a> •
  <a href="https://www.linkedin.com/company/phoenix-nap">LinkedIn</a> •
  <a href="https://www.instagram.com/phoenixnap">Instagram</a> •
  <a href="https://www.youtube.com/user/PhoenixNAPdatacenter">YouTube</a> •
  <a href="https://developers.phoenixnap.com/support">Email</a> 
</p>

<p align="center">
  <br>
  <a href="https://phoenixnap.com/bare-metal-cloud"><img src="https://user-images.githubusercontent.com/78744488/109779474-47222480-7c06-11eb-8ed6-91e28af3a79c.jpg" alt="phoenixnap Bare Metal Cloud"></a>
</p>
