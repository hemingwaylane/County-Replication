'''****************************************************************************
Name:        WILCOReplication.py
Description: This script prepares Round Rock's data for replication with WILCO 
Created by:  Nathan Smith
Date:		 September 2020
****************************************************************************'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import required modules        
import arcpy
from datetime import date
import time

# Set local variables
arcpy.env.workspace = "C:\\Users\\sbyrd\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\GISMASTER.sde"
workspace = arcpy.env.workspace
fcs = ['sde.ROUND_ROCK.address', 'sde.ROUND_ROCK.BUILDINGS', 'sde.ROUND_ROCK.CITY_FACILITIES', 'sde.ROUND_ROCK.PARCELS', 'sde.ROUND_ROCK.streets']
name = "UID"
script_expression = 'return nextSequenceValue ("Round_Rock.UIDGenerator")'
triggering_events = "INSERT"
description = "Used for UID Generation"
subtype = ""
field = "UID"
answer = None
answer2 = None
today = date.today()
rLog = "C:\\Users\\sbyrd\\City of Round Rock\\Information Technology Department - Department Files\\Geospatial Services\\Projects\\WILCO Replication\\ReplicationLog\\reconcilelog{}.txt".format(today)
t = 5
yes = ['Yes', 'yes', 'Y', 'y']
no = ['No', 'no', 'n', 'N']

#Ensure the administrator wants to disconnect all users
while answer not in ("Y", "N"): 
    answer = input("WARNING: This script will disconnect all users from sde@GISMASTER. All unsaved work will be lost. Are you sure you want to disconnect all users? (Y/N): ")
	
    if (answer in yes):
        #Disconnect all users from the database
        print("Disconnecting all users...")
        arcpy.DisconnectUser(workspace, "ALL")
        print("Users disconnected!")

        #Prevent connections to the database
        print("Preventing further connections...")
        arcpy.AcceptConnections(workspace, False)
        print("The database is no longer accepting connections.")
    
        # Loop through BASE feature classes and delete Attribute Rules
        print("\nAttribute Rules will be deleted from the following feature classes: ")
        print(fcs)
        print("Removing Attribute Rules...")
        for fc in fcs:
            print("Deleting Attribute Rule from " + fc)
            arcpy.DeleteAttributeRule_management(fc, name, "CALCULATION")
        print("Attribute Rules successfully removed!")
        
        #Reconcile and Post the RR_2_WILCO version
        print("\nReconciling and Posting RR_2_WILCO version to sde.DEFAULT...")
        arcpy.ReconcileVersions_management(workspace, "ALL_VERSIONS", "sde.DEFAULT", "RR_2_WILCO", "LOCK_ACQUIRED", "NO_ABORT", "BY_OBJECT", "FAVOR_TARGET_VERSION", "POST", "KEEP_VERSION", rLog)
        print("Reconciling and Posting Complete!")
		
        #Manually Synchronize Changes - Steve prefers to manually synchronize changes to review potential conflicts
        print("\r\nYou may now proceed with synchronizing changes. Please do not close this window.")
        time.sleep(5)
        input("\r\nOnce you have completed synchronizing changes, please press ENTER to continue...")
                        
        #Reconcile and Post the RR_2_WILCO version again
        print("Reconciling and Posting RR_2_WILCO version to sde.DEFAULT a second time...")
        arcpy.ReconcileVersions_management(workspace, "ALL_VERSIONS", "sde.DEFAULT", "RR_2_WILCO", "LOCK_ACQUIRED", "NO_ABORT", "BY_OBJECT", "FAVOR_TARGET_VERSION", "POST", "KEEP_VERSION", rLog)
        print("Second Reconciling and Posting Complete!")
                                
        #Loop through feature classes in specified dataset and run the AddAttributeRule tool
        print("\nRe-applying Attribute Rules to BASE...")
        for fc in fcs:
            print("Applying Attribute Rule to " + fc)
            arcpy.AddAttributeRule_management(fc, name, "CALCULATION", script_expression, "EDITABLE", triggering_events, "", "", description, subtype, field, "EXCLUDE")
        print("Attribute Rules successfully added!")
                                
        #Reallow connections to the database
        print("\nAllowing connections...")
        arcpy.AcceptConnections(workspace, True)
        print("The database is now accepting connections")
                                
        #Script complete
        print("Complete!")
        
    elif (answer in no): 
        print("Cancelling script execution...")
        exit() 
    else: 
        print("Stop being a schmuck. Please enter some form of Yes or No...\n") 

        
