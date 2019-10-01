@echo on
cd C:\Users\Jason\Desktop\PA3\LeafNode\bin
start ./main.py ..\conf\peer0.conf
start ./main.py ..\conf\peer1.conf
start ./main.py ..\conf\peer2.conf
start ./main.py ..\conf\peer3.conf
start ./main.py ..\conf\peer4.conf
start ./main.py ..\conf\peer5.conf
start ./main.py ..\conf\peer6.conf
start ./main.py ..\conf\peer7.conf
start ./main.py ..\conf\peer8.conf
start ./main.py ..\conf\peer9.conf
start ./main.py ..\conf\peer10.conf 
start ./main.py ..\conf\peer11.conf
start ./main.py ..\conf\peer12.conf 
start ./main.py ..\conf\peer13.conf "result4.txt"
timeout /t 1
start ./main.py ..\conf\peer14.conf
start ./main.py ..\conf\peer15.conf "result3.txt"
timeout /t 1
start ./main.py ..\conf\peer16.conf
start ./main.py ..\conf\peer17.conf "result1.txt"
timeout /t 1
start ./main.py ..\conf\peer18.conf
start ./main.py ..\conf\peer19.conf "result2.txt"
pause