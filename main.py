import json
import paramiko

servers_info = []

def execute_command(ssh, command):
    print("Executing:", command)
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    if error:
        print(f"Error executing {command}: {error}")
    return output

# Reading the JSON file
with open('test.json') as input_file:
    input_json = json.load(input_file)  # This will directly parse JSON into a dictionary

for server in input_json:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {server['ip']} as {server['username']}...")
        ssh.connect(server['ip'], username=server['username'], key_filename=server['ssh_key'])

        # Collect server details
        server_info = {
            "Ip": execute_command(ssh, "curl -s ifconfig.me"),
            "OS": execute_command(ssh, "cat /etc/os-release | grep PRETTY_NAME | cut -d '\"' -f2"),
            "Memory Usage": execute_command(ssh, "free -h | awk 'NR==2{print $3 \"/\" $2}'"),
            "Disk Usage": execute_command(ssh, "df -h --output=used,size / | tail -1"),
            "Running Processes": execute_command(ssh, "ps aux --no-headers | wc -l"),
            "Logged in Users": execute_command(ssh, "who"),
            "Open Ports": execute_command(ssh, "ss -tulnp | grep LISTEN"),
            "Uptime": execute_command(ssh, "uptime -p"),
            "Crons": execute_command(ssh, "crontab -l")
        }
        servers_info.append(server_info)

    except paramiko.SSHException as e:
        print(f"[FAILED] {server['ip']} - SSH Error: {e}")

    finally:
        ssh.close()

output_filename= "result.json"
with open(output_filename,'w') as output_file:
    json.dump(servers_info,output_file)