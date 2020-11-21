import sys
sys.path.append('../')

from Common_Libraries.p2_lib import *

import os
from Common_Libraries.repeating_timer_lib import repeating_timer

def update_sim ():
    try:
        arm.ping()
    except Exception as error_update_sim:
        print (error_update_sim)

arm = qarm()

update_thread = repeating_timer(2, update_sim)

from time import sleep
from random import shuffle
#Define a global dictionary in which to store the locations of the bins
bin_loc = {'effector_home': [0.4064, 0.0, 0.4826],
           'big_blue': [0.0, 0.383, 0.2781],
           'little_blue': [0.0, 0.6288, 0.3288],
           'big_red': [-0.3703, 0.1496, 0.3095],
           'little_red': [-0.5859, 0.2368, 0.3498],
           'big_green': [0.0, -0.383, 0.2781],
           'little_green': [0.0, -0.6288, 0.3288]}


def idBinLoc(container_id):
    #Get the bin_loc dictionary
    global bin_loc
    
    if container_id == 1: #Small Red
         drop_off = bin_loc['little_red']
    elif container_id == 2: #Small Green
        drop_off = bin_loc['little_green']
    elif container_id == 3: #Small Blue
        drop_off = bin_loc['little_blue']
    elif container_id == 4: #Big Red
        drop_off = bin_loc['big_red']
    elif container_id == 5: #Big Green
        drop_off = bin_loc['big_green']
    elif container_id == 6: #Big Blue
        drop_off = bin_loc['big_blue']
    else:
        print("That is not a valid shape ID.")
        arm.home()
    return drop_off


#moveEndEffector function to move the arm to the appropriate drop-off
def moveEndEffector(container_id, location):
    global bin_loc
    sleep(1)

    #Move to the pick-up location
    arm.move_arm(0.5,0,0.03)
    sleep(2)

    #Pick-up only when told to
    print("\nPlease flex your left arm to a value greater than 0.6.\n")
    controlGripper("close")

    #Open up the appropriate container drawer
    if container_id >= 4:
        print("\nPlease flex both arms fully.\n")
        openDrawer(container_id, True)

    #Return to the home position
    sleep(2)
    arm.move_arm(bin_loc['effector_home'][0],bin_loc['effector_home'][1],bin_loc['effector_home'][2])
    sleep(2)

    #Move to the drop-off
    arm.move_arm(location[0],location[1],location[2])
    sleep(2)

    #Drop-off only when told
    print("\nPlease extend your left arm to a value less than 0.6.\n")
    controlGripper("open")

    #Close the drawer and return home
    if container_id >= 4:
        print("\nPlease flex both arms fully.\n")
        openDrawer(container_id, False)
    
    sleep(2)
    arm.home()


#controlGripper closes/opens the gripper if the threshold has been crossed
def controlGripper(claw_action):
    #First check which action to execute
    if claw_action == "close":
        #Wait to be told to close the gripper
        while True:
            if arm.emg_left() > 0.6:
                #Close the gripper and carry on
                arm.control_gripper(55)
                break
    elif claw_action == "open":
        #Wait to be told to open the gripper
        while True:
            if arm.emg_left() < 0.6:
                #Open the gripper and carry on
                arm.control_gripper(-55)
                break
    else:
        print("That is not a valid value.")


#openDrawer function determines if a drawer needs to be opened or closed
def openDrawer(container_id, drawer_state):
    #A drawer state of True = closed drawer
    #A drawer state of False = open drawer

    while True:
        if arm.emg_left() == 1 and arm.emg_right() == 1:
            #Check Red Drawer
            if container_id == 4 and drawer_state == True:
                arm.open_red_autoclave(True)
            else:
                arm.open_red_autoclave(False)
        
            #Check Green Drawer
            if container_id == 5 and drawer_state == True:
                arm.open_green_autoclave(True)
            else:
                arm.open_green_autoclave(False)

            #Check Blue Drawer
            if container_id == 6 and drawer_state == True:
                arm.open_blue_autoclave(True)
            else:
                arm.open_blue_autoclave(False)

            break


def continueTerminate(reps):
    for i in reps:
        #Select a container to spawn, and get its corresponding drop-off
        bin_location = idBinLoc(i)
        arm.spawn_cage(i)
        sleep(0.5)

        #Pick-up and drop-off only when told
        print("\nPlease flex your right arm to a value greater than 0.6.\n")
        while True:
            if arm.emg_right() > 0.6:
                moveEndEffector(i, bin_location)
                break
        sleep(2)


def main():
    #Generate a shuffled list of values
    bin_id = [1,2,3,4,5,6]
    shuffle(bin_id)

    #Run the program until all containers have been stored
    continueTerminate(bin_id)
    print("This program is finished.")


main()
