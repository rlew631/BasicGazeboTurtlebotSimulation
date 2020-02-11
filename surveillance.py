#!/usr/bin/env python

from __future__ import print_function
import sys
import rospy
import cv2
from geometry_msgs.msg import Twist
from math import radians
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

class TakePhoto:
    def __init__(self):

        self.bridge = CvBridge()

        # Connect image topic
        img_topic = "/camera/rgb/image_raw"
        self.image_sub = rospy.Subscriber(img_topic, Image, self.callback)

        # Allow up to one second to connection
        rospy.sleep(1)

    def callback(self, data):

        # Convert image to OpenCV format
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        self.image = cv_image

    def take_picture(self, img_title):
        # Save an image
        cv2.imwrite(img_title, self.image)
        return True


def photo(num):
    camera = TakePhoto()

    # Take a photo
    # Use '_image_title' parameter from command line
    # Default value is 'photo.jpg'
    img_title = rospy.get_param('~image_title', 'photo' + str(num+1) + '.jpg')

    if camera.take_picture(img_title):
        rospy.loginfo("Saved image " + img_title)

    # Sleep to give the last log messages time to be sent
    rospy.sleep(1)


class Surveillance():
    def __init__(self):
        # initiliaze
        rospy.init_node('surveillance', anonymous=False)

        # What to do you ctrl + c    
        rospy.on_shutdown(self.shutdown)
        
        self.cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=10)
     
	# 5 HZ
        r = rospy.Rate(5);

	# create two different Twist() variables.  One for moving forward.  One for turning 45 degrees.

        # let's go forward at 0.2 m/s
        move_cmd = Twist()
        move_cmd.linear.x = 0.2
	# by default angular.z is 0 so setting this isn't required

        #let's turn at 45 deg/s
        turn_cmd = Twist()
        turn_cmd.linear.x = 0
        turn_cmd.angular.z = radians(45); #45 deg/s in radians/s

	#Go forward for 2 seconds (10 x 5 HZ) then turn for 2 second
	count = 0
        while not rospy.is_shutdown():
	    # go forward 0.4 m (2 seconds * 0.2 m / seconds)
	    rospy.loginfo("Going Straight")
            for x in range(0,5):
                self.cmd_vel.publish(move_cmd)
                r.sleep()
	    # turn 90 degrees
	    photo(count)
	    count = count + 1
	    if(count == 4): 
                break
	    rospy.loginfo("Turning")
            for x in range(0,11):
                self.cmd_vel.publish(turn_cmd)
                r.sleep()            

        
    def shutdown(self):
        # stop turtlebot
        rospy.loginfo("Surveillance finished")
        self.cmd_vel.publish(Twist())
        rospy.sleep(1)
 
if __name__ == '__main__':
    try:
        Surveillance()
    except:
        rospy.loginfo("node terminated.")


