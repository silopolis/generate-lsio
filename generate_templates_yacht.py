# Portainer App Templates for LinuxServer.io Docker containers
# Copyright (C) 2021  Technorabilia
# Written by Simon de Kraa <simon@technorabilia.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import os

import requests
import yaml
from jinja2 import Environment, FileSystemLoader

YACHT_ROOT = "/yacht"
YACHT_APPDATA = f"{YACHT_ROOT}/AppData"
VOLUMES_ROOT = f"{YACHT_ROOT}"

EXC_PARAM_VOL = [ \
    "/lib/modules", \
    "/opt/vc/lib", \
    "/run/udev:ro", \
    "/var/log", \
    "/var/run/docker.sock" \
    ]

def set_project_volumes(project_name,row):
    #TODO add '/config/*' support
    #TODO refactor volumes names case handling
    #TODO add support for ':ro'
    if row["vol_path"] == "/config" or row["vol_path"] == "/config/.minetest":
        row["vol_host_path"] = f"!config/{project_name}{row['vol_path']}"
        if row["desc"] == "": row["desc"] = "Container configuration volume"
        row["name"] = "Config"
    elif row["vol_path"] == "/data" or row["vol_path"] == "/datas":
        row["vol_host_path"] = "!datas"
        if row["desc"] == "": row["desc"] = "Datas volume"
        row["name"] = "Datas"
    elif row["vol_path"] == "/file" or row["vol_path"] == "/files":
        row["vol_host_path"] = "!files"
        if row["desc"] == "": row["desc"] = "Files volume"
        row["name"] = "Files"
    elif row["vol_path"] == "/media" or row["vol_path"] == "/medias":
        row["vol_host_path"] = "!medias"
        if row["desc"] == "": row["desc"] = "Media files volume"
        row["name"] = "Medias"
    elif row["vol_path"] == "/source" or row["vol_path"] == "/sources" \
         or row["vol_path"] == "/code":
        row["vol_host_path"] = "!sources"
        if row["desc"] == "": row["desc"] = "Sources volume"
        row["name"] = "Sources"
    elif row["vol_path"] == "/backup" or row["vol_path"] == "/backups":
        row["vol_host_path"] = "!backups"
        if row["desc"] == "": row["desc"] = "Backups volume"
        row["name"] = "Backups"
    elif row["vol_path"] == "/.snapshots":
        row["vol_host_path"] = "!snapshots"
        if row["desc"] == "": row["desc"] = "Backup snapshots volume"
        row["name"] = "Backup Snapshots"
    #Resilio-Sync
    elif row["vol_path"] == "/sync" or row["vol_path"] == "/Sync":
        row["vol_host_path"] = f"!sync/{project_name}"
        if row["desc"] == "": row["desc"] = "Synchronisation volume"
        row["name"] = "Resilio-Sync"
    #Syncthing
    elif row["vol_path"] == "/data1" or row["vol_path"] == "/data2":
        row["vol_host_path"] = f"!sync/{project_name}{row['vol_path']}"
        if row["desc"] == "": row["desc"] = "Synchronisation volume"
        row["name"] = "Syncthing"
    elif row["vol_path"] == "/picture" or row["vol_path"] == "/pictures" \
        or row["vol_path"] == "/photo" or row["vol_path"] == "/photos":
        row["vol_host_path"] = "!pictures"
        if row["desc"] == "": row["desc"] = "Pictures volume"
        row["name"] = "Pictures"
    #Photoshow
    elif row["vol_path"] == "/Pictures:ro":
        row["vol_host_path"] = "!pictures"
        if row["desc"] == "": row["desc"] = "Pictures volume (read-only)"
        row["name"] = "Pictures (read-only)"
    #Piwigo
    #https://github.com/Piwigo/Piwigo/issues/960
    elif row["vol_path"] == "/gallery" or row["vol_path"] == "/Gallery":
        row["vol_host_path"] = f"!pictures{row['vol_path']}"
        if row["desc"] == "": row["desc"] = "Piwigo pictures volume"
        row["name"] = "Piwigo Pictures"
    elif row["vol_path"] == "/music":
        row["vol_host_path"] = "!music"
        if row["desc"] == "": row["desc"] = "Music volume"
        row["name"] = "Music"
    elif row["vol_path"] == "/playlist" or row["vol_path"] == "/playlists":
        row["vol_host_path"] = "!playlists"
        if row["desc"] == "": row["desc"] = "Playlists volume"
        row["name"] = "Playlists"
    elif row["vol_path"] == "/podcast" or row["vol_path"] == "/podcasts":
        row["vol_host_path"] = "!podcasts"
        if row["desc"] == "": row["desc"] = "Podcasts volume"
        row["name"] = "Podcasts"
    elif row["vol_path"] == "/movie" or row["vol_path"] == "/movies" \
        or row["vol_path"] == "/data/movies":
        row["vol_host_path"] = "!movies"
        if row["desc"] == "": row["desc"] = "Movies volume"
        row["name"] = "Movies"
    elif row["vol_path"] == "/tv" or row["vol_path"] == "/tvshow" \
        or row["vol_path"] == "/tvshows" or row["vol_path"] == "/data/tvshows":
        row["vol_host_path"] = "!tv"
        if row["desc"] == "": row["desc"] = "TV shows volume"
        row["name"] = "TV"
    elif row["vol_path"] == "/recording" or row["vol_path"] == "/recordings":
        row["vol_host_path"] = "!recordings"
        if row["desc"] == "": row["desc"] = "Recordings volume"
        row["name"] = "Recordings"
    elif row["vol_path"] == "/download" or row["vol_path"] == "/downloads":
        row["vol_host_path"] = "!downloads"
        if row["desc"] == "": row["desc"] = "Downloads volume"
        row["name"] = "Downloads"
    elif row["vol_path"] == "/watch" or row["vol_path"] == "/Watch":
        row["vol_host_path"] = "!watched"
        if row["desc"] == "": row["desc"] = "Downloads watched volume"
        row["name"] = "Downloads Watched"
    elif row["vol_path"] == "/incomplete-downloads":
        row["vol_host_path"] =  f"!incomplete"
        if row["desc"] == "": row["desc"] = "Incomplete downloads volume"
        row["name"] = "Incomplete Downloads"
    elif row["vol_path"] == "/book" or row["vol_path"] == "/books":
        row["vol_host_path"] = "!books"
        if row["desc"] == "": row["desc"] = "Books volume"
        row["name"] = "Books"
    elif row["vol_path"] == "/comics":
        row["vol_host_path"] = "!comics"
        if row["desc"] == "": row["desc"] = "Comics volume"
        row["name"] = "Comics"
    elif row["vol_path"] == "/audiobook" or row["vol_path"] == "/audiobooks":
        row["vol_host_path"] = "!audiobooks"
        if row["desc"] == "": row["desc"] = "Audiobooks volume"
        row["name"] = "Audiobooks"
    elif row["vol_path"] == "/othermedia" or row["vol_path"] == "/othermedias":
        row["vol_host_path"] = "!othermedias"
        if row["desc"] == "": row["desc"] = "Other medias volume"
        row["name"] = "Other Medias"
    elif row["vol_path"] == "/thumbs" or row["vol_path"] == "/Thumbs" \
        or row["vol_path"] == "/thumbnails" or row["vol_path"] == "/Thumbnails":
        row["vol_host_path"] = "!thumbnails"
        if row["desc"] == "": row["desc"] = "Thumbnail pictures volume"
        row["name"] = "Thumbnails"
    # Netbootxyz
    elif row["vol_path"] == "/assets":
        row["vol_host_path"] = "!netboot"
        if row["desc"] == "": row["desc"] = "Netboot assets volume"
        row["name"] = "Netboot"
    else:
        row["vol_host_path"] = f"{YACHT_ROOT}/{project_name}{row['vol_path']}"

    return row


def get_project_vars(project_name):
    project_vars = init_vars.copy()

    vars_url = "https://raw.githubusercontent.com/linuxserver/docker-{}/master/readme-vars.yml".format(project_name)
    response = requests.get(vars_url)
    project_vars.update(yaml.load(response.text, Loader=yaml.FullLoader))

    # overrides
    project_vars["project_blurb"] = project_vars["project_blurb"].replace(
        "{{ project_name|capitalize }}", project_vars["project_name"].capitalize())
    project_vars["project_blurb"] = project_vars["project_blurb"].replace(
        "{{ project_name }}", project_vars["project_name"].capitalize())
    project_vars["project_blurb"] = project_vars["project_blurb"].replace(
        "{{ project_url }}", project_vars["project_url"])
    project_vars["project_blurb"] = project_vars["project_blurb"].replace(
        "\n", " ")
    project_vars["project_blurb"] = project_vars["project_blurb"].replace(
        '"', "'")
    project_vars["project_blurb"] = ' '.join(
        project_vars["project_blurb"].split())

    for row in project_vars["common_param_env_vars"]:
        if row["env_var"] == "PGID":
            row["env_value"] = "!PGID"
            row["desc"] = "for GroupID"
        if row["env_var"] == "PUID":
            row["env_value"] = "!PUID"
            row["desc"] = "for UserID"

    if project_vars["param_usage_include_vols"]:
        for row in project_vars["param_volumes"]:
            if f"{row['vol_path']}" not in EXC_PARAM_VOL:
                row = set_project_volumes(project_vars["project_name"],row)
                #print(f"{project_vars['project_name']}: volume: {row}")
    if project_vars["opt_param_usage_include_vols"]:
        for row in project_vars["opt_param_volumes"]:
            if f"{row['vol_path']}" not in EXC_PARAM_VOL:
                row = set_project_volumes(project_vars["project_name"],row)
                #print(f"{project_vars['project_name']}: opt volume: {row}")

    for row in project_vars["param_env_vars"]:
        if row["env_var"] == "TZ":
            row["env_value"] = "!TZ"
            row["desc"] = "Specify a timezone to use for example Europe/Amsterdam"

    if project_vars["project_logo"] == "http://www.logo.com/logo.png":
        project_vars["project_logo"] = ""

    if "full_custom_readme" in project_vars.keys() \
        and project_vars["full_custom_readme"] != "":
        project_vars["project_blurb"] = "This container needs special attention. Please check https://hub.docker.com/r/linuxserver/{} for details.".format(
            project_vars["project_name"])

    return project_vars


vars_url = "https://raw.githubusercontent.com/linuxserver/docker-jenkins-builder/master/vars/common"
resp = requests.get(vars_url)
init_vars = yaml.load(resp.text, Loader=yaml.FullLoader)

vars_url = "https://raw.githubusercontent.com/linuxserver/docker-jenkins-builder/master/vars/_container-vars-blank"
resp = requests.get(vars_url)
init_vars.update(yaml.load(resp.text, Loader=yaml.FullLoader))

env = Environment(loader=FileSystemLoader("templates"),
                  trim_blocks=True, lstrip_blocks=True)
env.globals.update(get_project_vars=get_project_vars)
template = env.get_template("templates-2.0-yacht.j2")


# Get full projects list
image_url = "https://fleet.linuxserver.io/api/v1/images"
response = requests.get(image_url)
response_json = response.json()


# Filter 'linuserver' repository projects
project_list = response_json["data"]["repositories"]["linuxserver"]
# Filter projects not deprecated
project_list = list(
    filter(lambda project: project["deprecated"] == False, project_list))
## Testing: filter single project
#project_list = list(
#    filter(lambda project: project["name"] == "wireguard", project_list))

for p in project_list:
    if p['category'] in [None, ""]:
        p['category'] = "FIXME"

projects = {
    "projects": project_list
}


out_filename = "templates-2.0.json"
with open(out_filename, "w") as out_file:
    out_file.write(template.render(projects))

# check valid json
with open(out_filename) as in_file:
    templates_v2 = json.load(in_file)

# check filesize
#if os.path.getsize(out_filename) < 200000:
#    raise Exception

out_filename = "templates-yacht.json"
templates_yacht = json.dumps(templates_v2["templates"], indent=2)
with open(out_filename, "w") as out_file:
    out_file.write(templates_yacht)

# check valid json
with open(out_filename) as in_file:
    templates_yacht_lint = json.load(in_file)

