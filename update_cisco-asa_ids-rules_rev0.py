#!/usr/bin/env python3

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

For more details, review a copy of the GNU General Public License at <https://www.gnu.org/licenses/>.

Created by: Leandro Fernandes Correia
Linkedin: https://www.linkedin.com/in/leo-correia/
GitHub: https://github.com/leo-fcorreia
Website: https://reptsec.com
Year: 2025

Description:
This script was developed to enhance the detection of events generated by syslog messages 
from the IDS (Intrusion Detection Service) of the Cisco ASA Firewall.

Disclaimer:
I am not responsible for the execution of these scripts, as they serve as a reference 
for improving detections. I highly recommend reviewing your rules and decoders in a 
test environment before applying them to production.

References:
- Wazuh Regex Documentation:
  https://documentation.wazuh.com/current/user-manual/ruleset/ruleset-xml-syntax/regex.html

- Cisco ASA Syslog Messages 4-4000nn:
  https://www.cisco.com/c/en/us/td/docs/security/asa/syslog/b_syslog/syslog-messages-400000-to-450001.html#con_4772079
"""


import os
import shutil

# File definition
FILE = "/var/ossec/ruleset/rules/0625-cisco-asa_rules.xml"
BACKUP_FILE = FILE + ".bak"

# Check if the file exists
if not os.path.isfile(FILE):
    print(f"Error: The file {FILE} was not found.")
    exit(1)

# Create a backup of the original file
shutil.copy(FILE, BACKUP_FILE)

# Read the file content line by line
with open(FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Control variables
new_lines = []
skip_rule_64016 = False
rule_64016_found = False

# Process the lines
for line in lines:
    if '<rule id="64016"' in line:
        skip_rule_64016 = True
        rule_64016_found = True
    if skip_rule_64016 and "</rule>" in line:
        skip_rule_64016 = False
        continue  # Skip this line to remove the rule
    if not skip_rule_64016:
        new_lines.append(line)

# Remove ", 64016" from rule <rule id="64017"> and eliminate trailing commas/spaces in <if_sid>
for i in range(len(new_lines)):
    if '<rule id="64017"' in new_lines[i]:
        for j in range(i, len(new_lines)):
            if "<if_sid>" in new_lines[j]:
                new_lines[j] = new_lines[j].replace(", 64016", "").replace("64016,", "").replace("64016", "")
                break

# Define the new rules to be added
new_rules = """
  <rule id="64034" level="12">
    <if_sid>64004</if_sid>
    <id>^4-400026|^4-400027|^4-400028</id>
    <description>ASA: TCP protocol manipulation Attack in progress detected.</description>
    <mitre>
      <id>T1071.001</id>
    </mitre>
    <group>ids,</group>
  </rule>

  <rule id="64035" level="12">
    <if_sid>64004</if_sid>
    <id>^4-400029|^4-400030</id>
    <description>ASA: FTP Improper Address or Port attack in progress detected.</description>
    <mitre>
      <id>T1071.002</id>
    </mitre>
    <group>ids,</group>
  </rule>

  <rule id="64036" level="12">
    <if_sid>64004</if_sid>
    <id>^4-400008</id>
    <description>ASA: IP impossible packet attack in progress detected.</description>
    <mitre>
      <id>T1090</id>
    </mitre>
    <group>ids,</group>
  </rule>

  <rule id="64037" level="12">
    <if_sid>64004</if_sid>
    <id>^4-400050</id>
    <description>ASA: Buffer Overflow attack in progress detected.</description>
    <mitre>
      <id>T1203</id>
    </mitre>
    <group>ids,</group>
  </rule>

  <rule id="64038" level="12">
    <if_sid>64004</if_sid>
    <id>^4-400007|^4-400009|^4-400023|^4-400024|^4-400025|^4-400031|^4-400032|^4-400033</id>
    <description>ASA: Network DoS attack in progress detected.</description>
    <mitre>
      <id>T1498</id>
    </mitre>
    <group>ids,</group>
  </rule>

  <rule id="64039" level="12">
    <if_sid>64004</if_sid>
    <id>^4-400041</id>
    <description>ASA: Proxied RPC Request attack in progress detected.</description>
    <mitre>
      <id>T1573</id>
    </mitre>
    <group>ids,</group>
  </rule>

  <rule id="64040" level="3">
    <if_sid>64004</if_sid>
    <id>^4-4000(\\d\\d)</id>
    <description>ASA: Unusual event detected.</description>
    <group>ids,</group>
  </rule>
"""

# Add the new rules after the last rule <rule id="64033">
insertion_index = next((i for i, line in enumerate(new_lines) if "<rule id=\"64033\"" in line), None)
if insertion_index is not None:
    while not new_lines[insertion_index].strip().endswith("</rule>"):
        insertion_index += 1
    insertion_index += 1  # Move to the line after </rule>
    new_lines.insert(insertion_index, new_rules + "\n")
    print("New rules added after the last rule 64033.")
    print("Rules 64034 to 64040 have been successfully added.")
else:
    print("Error: Could not locate <rule id=\"64033\"> to add rules.")
    exit(1)

# Write the changes to the file and read again for validation
with open(FILE, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Final validation
rules_removed = "<rule id=\"64016\">" not in content and "64016" not in content
missing_rules = [f"640{i}" for i in range(34, 41) if f"<rule id=\"640{i}\">" not in content]

if rules_removed:
    print("Rule 64016 was successfully removed.")
else:
    print(f"Error: The following rules were not found in the file: {', '.join(missing_rules)}")

if rules_removed:
    print("Changes applied successfully!")
else:
    print("Error modifying the file. Please check manually.")
    exit(1)
