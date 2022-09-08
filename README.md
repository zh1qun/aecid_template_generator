# aecid-template-generator
Create character-based templates for clustered log data

To get started, just clone this repository and execute
```
python3 template_generator.py
```
to run the aecid-template-generator with the default input file and configurations. To change the configuration, edit the template\_config.py file.

There are two sample configurations for pre-clustered Exim Mainlog and Messages log file. Just copy either of the configurations by
```
cp configs/template_config_mainlog.py template_config.py
```
or
```
cp configs/template_config_messages.py template_config.py
```
and then execute the main script as before.

More information on the aecid-template-generator is provided in the following paper :

Creating Character-based Templates for Log Data to Enable Security Event Classification
