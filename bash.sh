#!/bin/bash

############### A D M I N ############################################## INITIALIZATION #####################################################
command0='rm -rf ROOT/'
gnome-terminal --title="Deleting root" -x sh -c "$command0;"

sleep 1

command1='python3 AttributeCertifier.py --title "Identity Certificate" --name IdP --req-ip 127.0.0.1 --req-port 3001  --open-ip 127.0.0.1 --open-port 7001'

command2='python3 AttributeCertifier.py --title "Income Certificate" --name Employer --req-ip 127.0.0.1 --req-port 3002  --open-ip 127.0.0.1 --open-port 7002 --dependency "Identity Certificate"'

command3='truffle migrate --reset –compile-all'

gnome-terminal --title="Identity CA" -x sh -c "$command1 < Identity_input.txt;bash"
sleep 1
gnome-terminal --title="Income CA" -x sh -c "$command2 < Income_input.txt;bash"
sleep 1
gnome-terminal --title="SC Deploying" -x sh -c "$command3 > SC_output.txt;"
#bash avoided at tail end to exit the tab after execution
sleep 10 #waiting for SC deployment

Opening=$(sed -n '160p' SC_output.txt)
Issue=$(sed -n '161p' SC_output.txt)
Request=$(sed -n '162p' SC_output.txt)
Params=$(sed -n '163p' SC_output.txt)
Verify=$(sed -n '164p' SC_output.txt)

#echo $Params

command4='python3 ProtocolInitiator_DeployContracts.py --params-address $(grep "total cost:" SC_output.txt -A 7 | tail -6 | sed -e "1,3d;5,6d") --request-address $(grep "total cost:" SC_output.txt -A 7 | tail -6 | sed -e "1,2d;4,6d") --issue-address $(grep "total cost:" SC_output.txt -A 7 | tail -6 | sed -e "1d;3,6d") --opening-address $(grep "total cost:" SC_output.txt -A 7 | tail -6 | sed -e '2,6d') --accumulator-address $(grep "total cost:" SC_output.txt -A 7 | tail -6 | sed -e '1,5d')'

gnome-terminal --title="ProtocolInitiator_DeployContracts" -x sh -c "$command4;"
sleep 5

command5='python3 ProtocolInitiator_AC_Setup.py --title "Loan Credential" --name Loaner --ip 127.0.0.1 --port 4000 --dependency "Identity Certificate" "Income Certificate"'

gnome-terminal --title="ProtocolInitiator_AC_Setup" -x sh -c "$command5 < ProtocolInitiator_input.txt;"
sleep 5

command6='python3 ProtocolInitiator_UpdateCAInformation.py --titles "Identity Certificate" "Income Certificate" --address 0x6419B5373E351607530192844f47d36263F16d68 --rpc-endpoint "http://127.0.0.1:7546"'

gnome-terminal --title="ProtocolInitiator_UpdateCAInformation" -x sh -c "$command6;"
sleep 5

command7='python3 ProtocolInitiator_AnonymousCredentials.py --title "Loan Credential" --address 0x6419B5373E351607530192844f47d36263F16d68 --validator-addresses 0xc5E23FB5c7B09b95C9a8619cc115e00E91C5e338 0xc2887783932Fea8a7989D182B045892318578c36 0x0F2CE678b4dFe8A398bCD5dE4B6AE1C7743f3829 --opener-addresses 0x6dB18aF8c8c506a71c5E773D5F52aE5b2E02ef10 0x523b917bCc627B3d8e9D5cb2DC8704aeedFd33D6 0x478A7A228FfC3bfcDE841e8fEdE4B760e53F761b --rpc-endpoint "http://127.0.0.1:7546"'

gnome-terminal --title="ProtocolInitiator_AnonymousCredentials" -x sh -c "$command7;"
sleep 5

############### ############################################## #####################################################

command8='python3 Validator.py --title "Loan Credential" --id 1 --address 0xc5E23FB5c7B09b95C9a8619cc115e00E91C5e338 --rpc-endpoint "http://127.0.0.1:7546"'
command9='python3 Validator.py --title "Loan Credential" --id 2 --address 0xc2887783932Fea8a7989D182B045892318578c36 --rpc-endpoint "http://127.0.0.1:7546"'
command10='python3 Validator.py --title "Loan Credential" --id 3 --address 0x0F2CE678b4dFe8A398bCD5dE4B6AE1C7743f3829 --rpc-endpoint "http://127.0.0.1:7546"'

command11='python3 Opener.py --title "Loan Credential" --id 1 --ip 127.0.0.1 --port 8001 --address 0x6dB18aF8c8c506a71c5E773D5F52aE5b2E02ef10 --rpc-endpoint "http://127.0.0.1:7546"'
command12='python3 Opener.py --title "Loan Credential" --id 2 --ip 127.0.0.1 --port 8002 --address 0x523b917bCc627B3d8e9D5cb2DC8704aeedFd33D6 --rpc-endpoint "http://127.0.0.1:7546"'
command13='python3 Opener.py --title "Loan Credential" --id 3 --ip 127.0.0.1 --port 8003 --address 0x478A7A228FfC3bfcDE841e8fEdE4B760e53F761b --rpc-endpoint "http://127.0.0.1:7546"'

gnome-terminal --title="Validator 1" -x sh -c "$command8;bash"
gnome-terminal --title="Validator 2" -x sh -c "$command9;bash"
gnome-terminal --title="Validator 3" -x sh -c "$command10;bash"

gnome-terminal --title="Opener 1" -x sh -c "$command11;bash"
gnome-terminal --title="Opener 2" -x sh -c "$command12;bash"
gnome-terminal --title="Opener 3" -x sh -c "$command13;bash"

sleep 15
command14='python3 SP.py --title "Loan Service" --name Bank --address 0x0f166ee382eA8aaA1E48F319c7c4EF4656f23dd2 --verify-address $(grep "total cost:" SC_output.txt -A 7 | tail -6 | sed -e "1,4d;6d") --rpc-endpoint "http://127.0.0.1:7546" --accepts "Loan Credential"'

gnome-terminal --title="Service Provider" -x sh -c "$command14 < SP_input.txt;bash"
#gnome-terminal --title="Service Provider" -x sh -c "$command14;bash"

sleep 15

command15='python3 User.py --unique-name user1 --address 0x8DBf6Ebb3E99Ec42aF7A234FE01Ca78243844EA2 --rpc-endpoint "http://127.0.0.1:7546"'
gnome-terminal --title="User 1" -x sh -c "$command15 < User_input.txt;bash"
#gnome-terminal --title="User 1" -x sh -c "$command15;bash"

#python3 User.py --title "Loan Service" --name Bank --address 0x7a4Cd06dD4f8B58B274AB75c01310fDB5c75B56D --verify-address $(sed -n '164p' SC_output.txt) --accepts "Loan Credential" --unique-name user1 --address 0x1CF92f548B61b4dA87Dd372C19084a2B2bfA060f --rpc-endpoint "http://127.0.0.1:7545"


