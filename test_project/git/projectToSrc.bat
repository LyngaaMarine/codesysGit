cd ..
set location=%__CD__%
cd ..
"C:\\Program Files\\CODESYS 3.5.19.20\\CODESYS\\Common\\CODESYS.exe" --profile='CODESYS V3.5 SP19 Patch 2' --runscript='%__CD__%exporter.py' --scriptargs='%location%'
