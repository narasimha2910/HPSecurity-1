import os
import subprocess

machine_public_ip = input("Machine Public IP")
code_installation_dir = input("Full path to Code installation directory: ")
to_process_dir = input("Input( to process) Video clips directory full path: ")
processed_dir = input("Full path to directory where processed video will be saved: ")
git_key = input("Github personal access token (to generate: 'setting -> developer settings' on github): ")
postgres_user = input("Postgres user: ")
postgres_password = input("Postgres password: ")
postgres_db = input("Postgres database: ")
print("")
print("NOTE: <!> Github access token and postgres values will be included in plain text as part of the generated docker-compose.yml")
input("Press any key to continue...")

code_dir_name = "dcs-backend"
ui_code_dir_name = "dcs-frontend"
appserver_code_dir_name = "dcs-appserver"

#
proxy_ui_service_path = "\"/ui\""
appserver_service_path = "\"/appserver\""
app_server_base = f"http://{machine_public_ip}/appserver"
#

try:
    #creating required directories
    os.mkdir(code_installation_dir)
    print("Code installation directory has been created")

    os.mkdir(os.path.join(code_installation_dir, code_dir_name))
    os.mkdir(os.path.join(code_installation_dir, ui_code_dir_name))
    os.mkdir(os.path.join(code_installation_dir, appserver_code_dir_name))
    print("Code directories created")

    os.mkdir(to_process_dir)
    print("Input video directory created")

    os.mkdir(processed_dir)
    print("Processed video directory created")


    #create compose file using tmpl file and put it inside the code directory

    template_file = open("docker-compose.yml.tmpl", "r")
    docker_compose_file = open(os.path.join(code_installation_dir, "docker-compose.yml"), "w")

    for line in template_file.readlines():
        line=line.strip()
        fString = "f'{x}'".format(x=line)
        docker_compose_file.write(eval(fString) + "\n")

    template_file.close()
    docker_compose_file.close()
    print("Compose script generated")

    print("Creating conatainers, please wait...")
    with open(os.path.join(code_installation_dir, "output.log"), "a") as output:
        subprocess.call(f"cd {code_installation_dir} docker-compose pull && docker-compose build --pull && docker-compose up -d",
                        shell=True, stdout=output, stderr=output)

except OSError as e:
    print(e)


