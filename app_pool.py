import json
import paramiko
import concurrent.futures

def execute_command(ssh, command):
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
    output = ssh_stdout.read().decode().strip()
    error = ssh_stderr.read().decode().strip()
    return output if output else error

def fetch_server_info(server):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    server_info = {"IP Address": server['ip']}
    
    try:
        print(f"Connecting to {server['ip']} as {server['username']}...")
        ssh.connect(server['ip'], username=server['username'], key_filename=server['ssh_key'])
        
        server_info.update({
            "Ip": execute_command(ssh, "curl -s ifconfig.me"),
            "OS": execute_command(ssh, "cat /etc/os-release | grep PRETTY_NAME | cut -d '\"' -f2"),
            "Memory Usage": execute_command(ssh, "free -h | awk 'NR==2{print $3 \"/\" $2}'"),
            "Disk Usage": execute_command(ssh, "df -h --output=used,size / | tail -1"),
            "Running Processes": execute_command(ssh, "ps aux --no-headers | wc -l"),
            "Logged in Users": execute_command(ssh, "who"),
            "Open Ports": execute_command(ssh, "ss -tulnp | grep LISTEN"),
            "Uptime": execute_command(ssh, "uptime -p"),
            "Crons": execute_command(ssh, "crontab -l")
        })
        
        print(f"[SUCCESS] Data fetched for {server['ip']}")
    except paramiko.SSHException as e:
        print(f"[FAILED] {server['ip']} - SSH Error: {e}")
    finally:
        ssh.close()
    
    return server_info

# Reading the JSON file
with open('servers.json') as input_file:
    input_json = json.load(input_file)

servers_data = []

# Using ThreadPoolExecutor for parallel execution
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(fetch_server_info, input_json)
    servers_data.extend(results)

# Save the collected data to a JSON file in the same directory
output_filename = "server_metrics.json"
with open(output_filename, 'w') as output_file:
    json.dump(servers_data, output_file, indent=4)

print(f"All server data has been collected and saved to {output_filename}.")
