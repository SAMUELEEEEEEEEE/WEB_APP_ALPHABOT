import time
import RPi.GPIO as GPIO


class AlphaBot(object):
    
    def __init__(self, in1=13, in2=12, ena=6, in3=21, in4=20, enb=26):
        self.IN1 = in1      #destra avanti
        self.IN2 = in2      #destra indietro
        self.IN3 = in3      #sinistra indietro
        self.IN4 = in4      #sinistra avanti
        self.ENA = ena
        self.ENB = enb
        self.PA  = 50       #rotazione
        self.PB  = 50


        self.DR = 16
        self.DL = 19
        self.isRunning = True
        self.DL_status, self.DR_status = None, None
        self.sensor_dx_active = False
        self.sensor_sx_active = False
        self.sensor_all_active = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.DR,GPIO.IN,GPIO.PUD_UP)
        GPIO.setup(self.DL,GPIO.IN,GPIO.PUD_UP)

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.ENB, GPIO.OUT)
        self.PWMA = GPIO.PWM(self.ENA,500)
        self.PWMB = GPIO.PWM(self.ENB,500)
        self.PWMA.start(self.PA)
        self.PWMB.start(self.PB)
        self.stop()

    def left(self):
        self.PWMA.ChangeDutyCycle(self.PA)
        self.PWMB.ChangeDutyCycle(self.PB)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)

    def right(self):
        self.PWMA.ChangeDutyCycle(self.PA)
        self.PWMB.ChangeDutyCycle(self.PB)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)

    def forward(self, speed=30):
        self.PWMA.ChangeDutyCycle(speed)
        self.PWMB.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)

    def backward(self, speed=30):
        self.PWMA.ChangeDutyCycle(speed)
        self.PWMB.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)

    def stop(self):
        self.PWMA.ChangeDutyCycle(0)
        self.PWMB.ChangeDutyCycle(0)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.LOW)

    def get_sensor(self):
        self.DR_status = GPIO.input(self.DR)	#Statue of anterior right sensor
        self.DL_status = GPIO.input(self.DL)	#Statue of anterior left sensor
        # if DL_* == 1: not detention
        # if DL_* == 0: detention
        if((self.DL_status == 1) and (self.DR_status == 1)):
            self.sensor_dx_active = False
            self.sensor_sx_active = False
            self.sensor_all_active = False
            return("")

        elif((self.DL_status == 1) and (self.DR_status == 0)):
            #self.alphabot.stop()
            if self.sensor_dx_active is False:
                self.sensor_sx_active = False
                self.sensor_all_active = False
                return (f">> WARNING: anterior right sensor detetcts an obstacle!")
            #self.alphabot.left()
            #time.sleep(0.2)
            #self.alphabot.stop()
            self.sensor_dx_active = True

        elif((self.DL_status == 0) and (self.DR_status == 1)):
            #self.alphabot.stop()
            if self.sensor_sx_active is False:
                self.sensor_dx_active = False
                self.sensor_all_active = False
                return (f">> WARNING: anterior left sensor detetcts an obstacle!")
            #self.alphabot.right()
            #time.sleep(0.2)
            #self.alphabot.stop()
            self.sensor_sx_active = True
        else:
            #self.alphabot.stop()
            if self.sensor_all_active is False:
                self.sensor_dx_active = False
                self.sensor_sx_active = False
                return(f">> WARNING: anterior both sensors detetct an obstacle!")
            #self.alphabot.backward()
            #time.sleep(0.5)
            #self.alphabot.stop()
            self.sensor_all_active = True
        time.sleep(0.5)
        
    def set_pwm_a(self, value): #set the rotation
        self.PA = value
        self.PWMA.ChangeDutyCycle(self.PA)

    def set_pwm_b(self, value): #set the rotation
        self.PB = value
        self.PWMB.ChangeDutyCycle(self.PB)   
        
    def set_motor(self, left, right):
        if (right >= 0) and (right <= 100):
            GPIO.output(self.IN1, GPIO.HIGH)
            GPIO.output(self.IN2, GPIO.LOW)
            self.PWMA.ChangeDutyCycle(right)
        elif (right < 0) and (right >= -100):
            GPIO.output(self.IN1, GPIO.LOW)
            GPIO.output(self.IN2, GPIO.HIGH)
            self.PWMA.ChangeDutyCycle(0 - right)
        if (left >= 0) and (left <= 100):
            GPIO.output(self.IN3, GPIO.HIGH)
            GPIO.output(self.IN4, GPIO.LOW)
            self.PWMB.ChangeDutyCycle(left)
        elif (left < 0) and (left >= -100):
            GPIO.output(self.IN3, GPIO.LOW)
            GPIO.output(self.IN4, GPIO.HIGH)
            self.PWMB.ChangeDutyCycle(0 - left)


if __name__ == '__main__':

    Ab = AlphaBot()
    Ab.forward()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()
