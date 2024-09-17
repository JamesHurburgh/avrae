<drac2>

# Get the args
args = argparse("&*&")

# Setup the variable names
cc_upgradeProgress = "Brisbandit Gentrification"
cc_location = "Brisbandit Location Level"
cvar_upgradeLog = "location_upgrade_log"
cvar_levelLog = "location_level_log"
cvar_locationName = "Brisbandit_Location_Name"
default_locationName = f"{name}'s location"
cvar_locationDesc = "Location_Desc"
default_locationDesc = "A nice location to be at."
cvar_lastIncome = "location_lastIncome"

# timing
ticks_per_week = 60 * 60 * 24 * 7
reset_epoch = 1679670000
current_time = time()
last_reset = floor((current_time - reset_epoch) / ticks_per_week) * ticks_per_week + reset_epoch
next_reset = last_reset + ticks_per_week

# Setup some lookups
sizeChart = {
    1: "A small secure room protected from the weather (10ft x 10ft). eg. A tiny cottage or hut, a residence for a single person or a small family, a workspace, such as a blacksmith's forge or a woodworker's shop",
    2: "A tiny building (20ft x 20ft). eg. Small cottage, a one-room chapel, or a guard tower.",
    3: "A small building (30ft x 30ft). eg. Medium cottage or a one-room tavern.",
    4: "A moderate building (40ft x 40ft). eg. Small chapel or a peasant's house.",
    5: "A large building (50ft x 50ft). eg. Town meeting hall",
    6: "A huge building (60ft x 60ft).",
    7: "A massive building (70ft x 70ft).",
    8: "A enormous building (80ft x 80ft).",    
}

# Alias the character
ch=character()

# Start building the embed
embed = []
embed.append("embed")
aliasActions = []

# Ensure the counters exist
ch.create_cc_nx(cc_upgradeProgress, 0, 4, "none", "bubble", None, None, cc_upgradeProgress, cc_upgradeProgress, 0)
ch.create_cc_nx(cc_location , 0, None, "none", None, None, None, cc_location, cc_location, 0)

# Get and/or set the name
location_name = args.last('name') or ch.get_cvar(cvar_locationName) or default_locationName
if ch.get_cvar(cvar_locationName) != location_name:
  ch.set_cvar(cvar_locationName, location_name.replace("\"", "\\\""))
  aliasActions.append(f"{name} changed their location name to '{location_name}'.")

# Get and/or set the description
location_desc = args.last('desc') or ch.get_cvar(cvar_locationDesc) or default_locationDesc
if ch.get_cvar(cvar_locationDesc) != location_desc :
  ch.set_cvar(cvar_locationDesc, location_desc )
  aliasActions.append(f"{name} changed their location description to '{location_desc}'.")

# Do a skill check to try to upgrade the location
if args.last("skill"):
  dc = ch.get_cc(cc_location) + 10
  skill = args.last('skill')
  skill_mod = ch.skills[skill].value
  result = vroll(f"1d20+{skill_mod}")
  skillCheckTitle = f"\n{name} makes a {skill} check to attempt a **DC{dc}** location upgrade.".replace("'","\\'").replace('"','\\"')
  skillCheckResult = f"\n {result.full}"
  success = result.total >= dc
  if success:
    ch.mod_cc(cc_upgradeProgress, 1)
    skillCheckResult += f"\n⭐ {name} made progress upgrading their location."
    ch.set_cvar(cvar_upgradeLog, f"{ch.get_cvar(cvar_upgradeLog) or ''}<t:{int(time())}> **Pass!** {skill} {result.full}\n")
    if ch.get_cc(cc_upgradeProgress) == 4:
      ch.set_cc(cc_upgradeProgress, 0)
      ch.mod_cc(cc_location, 1)
      skillCheckResult += f"\n🌟 {name} upgraded their location to level {ch.get_cc(cc_location)}."
      ch.set_cvar(cvar_levelLog, f"{ch.get_cvar(cvar_levelLog) or ''}<t:{int(time())}> Level {ch.get_cc(cc_location)}\n")
      ch.set_cvar(cvar_upgradeLog, "")
  else:
    ch.set_cvar(cvar_upgradeLog, f"{ch.get_cvar(cvar_upgradeLog) or ''}<t:{int(time())}> **Fail** {skill} {result.full}\n")
  skillCheckResult = skillCheckResult.replace("'","\\'").replace('"','\\"')
  embed.append(f"-f '{skillCheckTitle}|{skillCheckResult}'")
  if success and ch.get_cc(cc_upgradeProgress) == 0:
    embed.append(f"-f 'Level Log|{ch.get_cvar(cvar_levelLog)}'")
  else:
    embed.append(f"-f 'Upgrade Log|{ch.get_cvar(cvar_upgradeLog)}'")

# Generate income
if args.last("income"):
  locationLevel = ch.get_cc(cc_location)
  lastIncome = ch.get_cvar(cvar_lastIncome)
  if locationLevel < 1:
    embed.append(f"-f 'No income|Location must be at least level one to generate income.  Try upgrading it using `!location -skill <skill name>`'")
  elif lastIncome is not None and lastIncome.strip() and floor(lastIncome) > last_reset:
    embed.append(f"-f 'No more income|Income was already received this week on <t:{floor(lastIncome)}>.  Wait until <t:{next_reset}>.'")
  else:
    ch.set_cvar(cvar_lastIncome, time())
    locationIncomeDice = ch.get_cc(cc_location)
    characterIncomeDice = ch.levels.total_level
    totalIncomeDice = locationIncomeDice + characterIncomeDice
    incomeDescription = f"(location level({locationIncomeDice}) + character level({characterIncomeDice}))d4"
    incomeRoll = f"{totalIncomeDice}d4"
    incomeResult = vroll(incomeRoll)
    ch.coinpurse.modify_coins(gp = incomeResult.total)
    embed.append(f"-f 'Income|{incomeDescription}\n{incomeResult}\n+{incomeResult.total}gp\n{ch.coinpurse}'")


# Add the log if called for
if args.last("log"):
  embed.append(f"-f 'Upgrade Log|{ch.get_cvar(cvar_upgradeLog)}'")
  embed.append(f"-f 'Level Log|{ch.get_cvar(cvar_levelLog)}'")
  if ch.get_cvar(cvar_lastIncome) is not None and ch.get_cvar(cvar_lastIncome).strip():
    embed.append(f"-f 'Income|Last generated <t:{floor(ch.get_cvar(cvar_lastIncome))}>'")
  embed.append(f"-f 'Last reset|<t:{last_reset}>'")
  embed.append(f"-f 'Next reset|<t:{next_reset}>'")

# Reset if called for
if args.last("reset"):
  aliasActions.append(f"**RESETING**")
  aliasActions.append(f"{cc_upgradeProgress}: **{ch.get_cc(cc_upgradeProgress)}**")
  ch.set_cc(cc_upgradeProgress, 0)
  aliasActions.append(f"{cc_location}: **{ch.get_cc(cc_location)}**")
  ch.set_cc(cc_location, 0)
  aliasActions.append(f"{cvar_upgradeLog}: **{ch.get_cvar(cvar_upgradeLog) or '-'}**")
  ch.set_cvar(cvar_upgradeLog, "")
  aliasActions.append(f"{cvar_levelLog}: **{ch.get_cvar(cvar_levelLog) or '-'}**")
  ch.set_cvar(cvar_levelLog, "")
  aliasActions.append(f"{cvar_locationName}: **{ch.get_cvar(cvar_locationName)}**")
  ch.set_cvar(cvar_locationName, "")
  aliasActions.append(f"{cvar_locationDesc}: **{ch.get_cvar(cvar_locationDesc)}**")
  ch.set_cvar(cvar_locationDesc, "")
  aliasActions.append(f"{cvar_lastIncome}: **{ch.get_cvar(cvar_lastIncome)}**")
  ch.set_cvar(cvar_lastIncome, "")
  
# Create the title
title = location_name.replace("'","\\'").replace('"','\\"')
if (ch.cc_exists(cc_location) and ch.get_cc(cc_location) > 0):
  title += f" (Level {ch.cc_str(cc_location)})"
embed.append(f"-title '{title}'")

# Create the description
if args.last("status"):
  description = location_desc.replace("'","\\'").replace('"','\\"')
  embed.append(f"-desc '{description}'")
  size = ch.get_cc(cc_location)
  if size > 0:
    embed.append(f"-f 'Size|{sizeChart[size]}'")
  
# Add actions
if (len(aliasActions) > 0):
  actionText = "\n".join(aliasActions).replace('"','\\"')
  embed.append(f"-f 'Actions|{actionText}'")

embed.append(f"-thumb '{ch.image}'")
embed.append("-footer '!location | Made by James Hurburgh#6265'")

return "\n".join(embed)
</drac2>