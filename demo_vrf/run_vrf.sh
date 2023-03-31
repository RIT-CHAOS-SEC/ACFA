echo "Starting symbolic execution to get expected CF...."
# swap to angr environment
source ~/angr/bin/activate

# Generate static/expected cf
python3 symbolic_exec.py > symb_exec.log

echo "Done. Check 'sim.cflog' and 'symb_exec.log' for script output"

echo "--------------------"
echo "Starting protocol..."
# start vrf protocol
sudo python3 serialComms.py > prot.log

# exit angr environment
deactivate

echo "Complete. Check #.cflog files for CF-Logs from PRV. Check 'prot.log' for script output"