
#include <unistd.h> //getopt
#include <stdlib.h> //atoi, exit
#include <string.h> //memset, strncpy


#include <fcntl.h>
#include <linux/input.h>
#include <linux/uinput.h>
#include <stdio.h>


static unsigned int ascii2keycode1[128] = {
           0,  0,  0,  0,  
           0,  0,  0,  0,  
           0,  0,  0,  0,  
	   0,  0,  0,  0,  

           0,  0,  0,  0,  
           0,  0,  0,  0,  
           0,  0,  0,  0,  
           0,  0,  0,  0,  

	   0, KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, 
	   KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, 0, 
	   KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, 
	   0,0,  0,  0, 

           0,  0,  0,  0,  
           0,  0,  0,  0,  
           0,  0,  KEY_LEFTSHIFT,  0,  
           KEY_LEFTSHIFT,  0,  KEY_LEFTSHIFT,   KEY_LEFTSHIFT, 

	   KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, 
	   KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, 
	   KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, 
	   KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, 

	   KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, 
	   KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, 
	   KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, 0, 
	   0, 0, KEY_LEFTSHIFT, KEY_LEFTSHIFT, 

           0,  0,  0,  0,  
           0,  0,  0,  0,  
           0,  0,  0,  0,  
	   0,  0,  0,  0,  

           0,  0,  0,  0,  
           0,  0,  0,  0,  
           0,  0,  0,   KEY_LEFTSHIFT, 
	   KEY_LEFTSHIFT, KEY_LEFTSHIFT, KEY_LEFTSHIFT, 0
};

static unsigned int ascii2keycode2[128] = {
           0,  0,  0,  0,  
	   0,  0,  0,  0,  
	   KEY_BACKSPACE,  KEY_TAB,  0,  0,  
	   0,  KEY_ENTER,  0,  0,

           0,  0,  0,  0,  
           0,  0,  0,  0,  
           0,  0,  0,  KEY_ESC,  
           0,  0,  0,  0,  

	   KEY_SPACE, KEY_1, KEY_APOSTROPHE, KEY_3,
	   KEY_4, KEY_5, KEY_7, KEY_APOSTROPHE, 
	   KEY_9, KEY_0, KEY_8, KEY_EQUAL,
	   KEY_COMMA, KEY_MINUS, KEY_DOT, KEY_SLASH, 

	   KEY_0, KEY_1, KEY_2, KEY_3,
	   KEY_4, KEY_5, KEY_6, KEY_7,
	   KEY_8, KEY_9, KEY_SEMICOLON, KEY_SEMICOLON,
	   KEY_COMMA, KEY_EQUAL, KEY_DOT, KEY_SLASH, 

	   KEY_2, KEY_A, KEY_B, KEY_C,
	   KEY_D, KEY_E, KEY_F, KEY_G,
	   KEY_H, KEY_I, KEY_J, KEY_K,
	   KEY_L, KEY_M, KEY_N, KEY_O,
	   
	   KEY_P, KEY_Q, KEY_R, KEY_S,
	   KEY_T, KEY_U, KEY_V, KEY_W,
	   KEY_X, KEY_Y, KEY_Z, KEY_LEFTBRACE,
	   KEY_BACKSLASH, KEY_RIGHTBRACE, KEY_6, KEY_MINUS,

	   KEY_GRAVE, KEY_A, KEY_B, KEY_C,
	   KEY_D, KEY_E, KEY_F, KEY_G,
	   KEY_H, KEY_I, KEY_J, KEY_K,
	   KEY_L, KEY_M, KEY_N, KEY_O,
	   
	   KEY_P, KEY_Q, KEY_R, KEY_S,
	   KEY_T, KEY_U, KEY_V, KEY_W,
	   KEY_X, KEY_Y, KEY_Z, KEY_LEFTBRACE,
	   KEY_BACKSLASH, KEY_RIGHTBRACE, KEY_GRAVE, KEY_DELETE
};


  int uinp_fd;
  struct uinput_user_dev uinp;       // uInput device structure
  struct input_event event; // Input device structure

int setup_uinput_device()
{
  
         // Temporary variable
         int i=0;
         uinp_fd = -1;
 
        // Open the input device
         uinp_fd = open("/dev/input/uinput", O_WRONLY | O_NDELAY);
         if (uinp_fd == 0)
         {
                printf("Unable to open /dev/input/uinput\n");
                return -1;
       }

	 //printf("%d", uinp_fd);

       memset(&uinp,0,sizeof(uinp)); // Intialize the uInput device to NULL
       strncpy(uinp.name, "opengazer", UINPUT_MAX_NAME_SIZE);
       uinp.id.version = 0;
       uinp.id.bustype = 0;
       //dev_mouse.id.vendor = BTNX_VENDOR;
       //dev_mouse.id.product = BTNX_PRODUCT_MOUSE;
       
       // Setup the uinput device
       ioctl(uinp_fd, UI_SET_EVBIT, EV_KEY);
             ioctl(uinp_fd, UI_SET_EVBIT, EV_REL);
       ioctl(uinp_fd, UI_SET_RELBIT, REL_X);
       ioctl(uinp_fd, UI_SET_RELBIT, REL_Y);

       /*ioctl(uinp_fd, UI_SET_EVBIT, EV_ABS);
       ioctl(uinp_fd, UI_SET_ABSBIT, ABS_X);
       ioctl(uinp_fd, UI_SET_ABSBIT, ABS_Y);
       */
		uinp.absmin[ABS_X] = -100;
		uinp.absmax[ABS_X] = 100;
		uinp.absmin[ABS_Y] = -100;
		uinp.absmax[ABS_Y] = 100;
		uinp.absfuzz[ABS_X] = 3;
		uinp.absfuzz[ABS_Y] = 3;
		uinp.absflat[ABS_X] = 0;
		uinp.absflat[ABS_Y] = 0;

       for (i=0; i < 256; i++) {
                  ioctl(uinp_fd, UI_SET_KEYBIT, i);
       }
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_MOUSE);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_TOUCH);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_MOUSE);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_LEFT);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_MIDDLE);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_RIGHT);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_FORWARD);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_BACK);

       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_SIDE);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_EXTRA);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_TASK);

       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_JOYSTICK);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_TRIGGER);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_THUMB);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_THUMB2);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_TOP);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_TOP2);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_PINKIE);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_BASE);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_BASE2);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_BASE3);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_BASE4);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_BASE5);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_BASE6);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_DEAD);

       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_MISC);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_0);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_1);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_2);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_3);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_4);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_5);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_6);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_7);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_8);
       ioctl(uinp_fd, UI_SET_KEYBIT, BTN_9);

       for (i=128; i < 195; i++) {
                  ioctl(uinp_fd, UI_SET_KEYBIT, i);
       }

       ioctl(uinp_fd, UI_SET_KEYBIT, KEY_COFFEE);
       ioctl(uinp_fd, UI_SET_KEYBIT, KEY_COFFEE);
       ioctl(uinp_fd, UI_SET_KEYBIT, KEY_COFFEE);
       ioctl(uinp_fd, UI_SET_KEYBIT, KEY_COFFEE);
       ioctl(uinp_fd, UI_SET_KEYBIT, KEY_COFFEE);
       ioctl(uinp_fd, UI_SET_KEYBIT, KEY_COFFEE);
       ioctl(uinp_fd, UI_SET_KEYBIT, KEY_COFFEE);









       // Create input device into input sub-system
       write(uinp_fd, &uinp, sizeof(uinp));
       if (ioctl(uinp_fd, UI_DEV_CREATE))
       {
                printf("Unable to create UINPUT device.");
                return -1;
       }

       return 1;

}

int destroy_uinput_device()
{
  ioctl(uinp_fd, UI_DEV_DESTROY);
  close(uinp_fd);
}

void press(__u16 key, __s32 value) {
		  if (value) {

		    /*   printf("%d\n", key); */
		  memset(&event, 0, sizeof(event));
		  gettimeofday(&event.time, NULL);
		  event.type = EV_KEY;
		  event.code = key;
		  event.value = 1;
		  write(uinp_fd, &event, sizeof(event));
		  event.type = EV_SYN;
		  event.code = SYN_REPORT;
		  event.value = 0;
		  write(uinp_fd, &event, sizeof(event));
		  } 
		  else {
		  // Report BUTTON PRESS - RELEASE event
		  memset(&event, 0, sizeof(event));
		  gettimeofday(&event.time, NULL);
		  event.type = EV_KEY;
		  event.code = key;
		  event.value = 0;
		  write(uinp_fd, &event, sizeof(event));
		  event.type = EV_SYN;
		  event.code = SYN_REPORT;
		  event.value = 0;
		  write(uinp_fd, &event, sizeof(event));
		  }

}

void press1(__u16 key) {
  press(key, (__s32) 1);
  press(key, (__s32) 0);
}


void pressN(__u16 *keycodes, int len) {
  int i;
  for (i=0; i<len; i++) {
    /*printf("%d\n", keycodes[i]);*/
    press(keycodes[i], (__s32) 1);
  }
  for (i=len-1; i>=0; i--) {
    press(keycodes[i], (__s32) 0);
  }
}

void press2(__u16 key1, __u16 key2) {
__u16 keycodes[3];
 keycodes[0]=key1; keycodes[1]=key2;
 pressN(keycodes, 2);

  /*  press(key1, (__s32) 1);
  press(key2, (__s32) 1);
  press(key2, (__s32) 0);
  press(key1, (__s32) 0);*/
}


int char2keycodes(char c, __u16 *keycodes) {
  int len;

  /*  printf("%d\n", (int) c);  */

  len = 0;
  keycodes[len] = ascii2keycode1[(int) c];
  if (keycodes[len]) {len=len+1;}
  keycodes[len] = ascii2keycode2[(int) c];
  if (keycodes[len]) {len=len+1;}

  return len;
}


void press_char_from_table(char c) {
  __u16 keycodes[2];
  int i;

  /*  printf("%d\n", (int) c);  */

  i = 0;

  i = i + char2keycodes(c, keycodes);

  /*keycodes[i] = ascii2keycode1[(int) c];
  if (keycodes[i]) {i=i+1;}
  keycodes[i] = ascii2keycode2[(int) c];
  if (keycodes[i]) {i=i+1;}*/

  if (i == 1) {press1(keycodes[0]);}
  if (i == 2) {press2(keycodes[0], keycodes[1]);}
}




int main( int argc, char **argv)
{
  

  __u16 keycodes[256]; /* todo: mb segfault if user puts in too many */
  int i;
  char optch;

  /*  printf("%d\n", (int) c);  */

  i = 0;
	static char optstring[] = "k:c:";

	while ( -1 != (optch = getopt( argc, argv, optstring)) ) {
		switch ( optch ) {
			case 'k' :
				keycodes[i++] = atoi(optarg);
				/* printf("%d\n",atoi(optarg) );  */
				break;
			case 'c' :
			  i = i + char2keycodes(optarg[0], keycodes + i);
				break;
		}
	}

  /* is this really a keycode? */
  /*  int keycode;
  keycode = atoi(argv[1]);
  */


	setup_uinput_device(); destroy_uinput_device();
	  setup_uinput_device(); destroy_uinput_device();
	  setup_uinput_device(); destroy_uinput_device();
	  setup_uinput_device();
	  /*press2(keycode);*/

	  if  (i) {
	    /*	    press2((__u16) keycodes[0], (__u16) keycodes[1]);*/
	    pressN(keycodes, i);
	  }
	  else {
	    press_char_from_table(argv[1][0]);
	  }

	  destroy_uinput_device();

	return 0;

}
