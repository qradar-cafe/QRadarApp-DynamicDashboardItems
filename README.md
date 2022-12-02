# RESTMethod

This sample app demonstrates how to use an app *REST method* to populate a pulse dashboard in QRadar. 

## Running this app

You can package this app and deploy it by executing in this directory:

```bash
docker run -v $(pwd)/container/pip:/pip registry.access.redhat.com/ubi8/python-36 pip download --no-deps --dest /pip pandas pytz python-dateutil numpy openpyxl et-xmlfile docxtpl python-docx docxcompose matplotlib pillow cycler kiwisolver

qapp package -p app.zip
```

and

```bash
qapp deploy -p app.zip -q <qradar console ip> -u <qradar user>
```
