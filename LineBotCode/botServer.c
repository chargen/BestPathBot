/**
 *  Robot Server for "Best Path" problem
 *  This program facilitates cross-communication between
 *      "Best Path" problem solving entities
 *  @syntax : ./botServer [ PORT NUMBER ]
 *  @note   : good path = 1, bad path = 0
 *  @author : Dandy Martin
 **/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/wait.h>
#include <string.h>
#include <time.h>
#include <errno.h>
#include <pthread.h>

#define MAX_CLIENTS 10
#define MAX_LINE_LENGTH 50
#define ERROR_MARGIN 3
#define MAX_COLORS 5
#define LOG_FILE ((const unsigned char *) "/tmp/pathlog.txt")


///Prototypes:
void handle_client(int fd);

///Global Variables:
int color_list[MAX_COLORS][2];
static int clientno = 0, color_count = 0, good_path = 0;
static pthread_mutex_t mtx = PTHREAD_MUTEX_INITIALIZER;

///error method
void error(char *msg){
    perror(msg);
    exit(1);
}



int main(int argc, char *argv[]){

    unsigned int sockfd, newsockfd, portno, clilen;
    pthread_t threadID;                                             //thread id
    struct sockaddr_in serv_addr, cli_addr;

    if(argc < 2){
        fprintf(stderr, "ERROR, no port provided\n");
        exit(1);
    }

    if((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0){

        error("ERROR opening socket");

    }

    bzero((char *) &serv_addr, sizeof(serv_addr));

    portno = atoi(argv[1]);

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = INADDR_ANY;
    serv_addr.sin_port = htons(portno);

    if(bind(sockfd, (struct sockaddr * ) & serv_addr, sizeof(serv_addr)) < 0){
        error("ERROR on binding");
    }

    listen(sockfd, 5);
    clilen = sizeof(cli_addr);

    ///Create new thread to run handle_client() upon client acceptance
    while(1){

        if((newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen)) < 0){
            error("ERROR on accept");
        }else{
            pthread_create(&threadID, NULL, handle_client, newsockfd);
        }
    }

   return 0;

}

/**
 *  Exchange information with client and maintain color_list[][] array
 *  @param : nsfd - socket file descriptor
 *  @return : void
 **/
void handle_client(int nsfd){

    char buffer[256];                                               //buffer for sending-receiving messages
    char *ptr;
    int clr_temp;
    int loc;
    pthread_mutex_lock(&mtx);
    	const int cID = clientno++;
    pthread_mutex_unlock(&mtx);
    int pathflag;
    int n;

    while(1){

        int enc = 0;
        bzero(buffer, 256);

        if((n = read(nsfd, buffer, 255)) < 0){
            error("ERROR reading from socket: Initial read");
        }
        strtok (buffer, "\n");

        if((n = strcmp(buffer, "C")) == 0){                         //prepare to receive color
            bzero(buffer, 256);
            if((n = write(nsfd, "R", 1)) < 0){                      //send ready
                error("ERROR writing to socket: Send Ready");
            }
            if((n = read(nsfd, buffer, 255)) < 0){
                error("ERROR reading from socket: Color Read");
            }

            strtok (buffer, "\n");
            clr_temp = strtol(buffer, &ptr, 10);
            bzero(buffer, 256);
            pthread_mutex_lock(&mtx);
                pathflag = good_path;
            pthread_mutex_unlock(&mtx);
            ///If a good path has not already been found, search list for match on read color
            ///If no color has been encountered yet, skip for-loop contents altogether
            ///Else, set encountered flag without search
            if(!pathflag){
                pthread_mutex_lock(&mtx);
                for(int i = 0; i < color_count; i++){
                    if(clr_temp >= (color_list[i][0] - ERROR_MARGIN) &&
                                    clr_temp <= (color_list[i][0] + ERROR_MARGIN)){
                        enc = 1;
                        loc = i;
                    }
                }
                pthread_mutex_unlock(&mtx);
            }else{
                enc = 1;
                printf("GOOD PATH ALREADY FOUND: %d\n", pathflag);
            }
                ///If color has not been encountered, add it to color_list[][] array
                ///Send "Not Encountered" flag to client and wait on path results
                ///Add path ranking to read color's location in the array
                if(!enc){
                    printf("Color value: %d\n", clr_temp);
                    pthread_mutex_lock(&mtx);
                        color_list[color_count][0] = clr_temp;
                        color_count++;
                        printf("COLORS READ: %d\n", color_count);
                    pthread_mutex_unlock(&mtx);
                    if((n = write(nsfd, "N", 1)) < 0){              //send not encountered
                        error("ERROR writing to socket");
                    }
                    printf("Client: %d. %d not encountered. Waiting on path ranking...\n", cID, clr_temp);
                    bzero(buffer, 256);
                    if((n = read(nsfd, buffer, 255)) < 0){          //read if color not encountered
                        error("ERROR reading from socket");
                    }
                    strtok (buffer, "\n");
                    if((n = strcmp(buffer, "B")) == 0){
                        printf("BAD PATH: %d\n", clr_temp);
                        pthread_mutex_lock(&mtx);
                            color_list[color_count - 1][1] = 0;
                        pthread_mutex_unlock(&mtx);
                    }else if ((n = strcmp(buffer, "G")) == 0){
                        printf("GOOD PATH: %d\n", clr_temp);
                        pthread_mutex_lock(&mtx);
                            color_list[color_count - 1][1] = 1;
                            good_path = clr_temp;                   //sets good_path value to read color
                        pthread_mutex_unlock(&mtx);
                        printf("GOOD PATH FOUND\n");
                    }
                ///If color has been encountered already by bots, send "Encountered" flag
                ///and their "good" or "bad" ranking (or send NULL if path reading is not complete)
                ///If good color has been found send "good" ranking, and good color value
                }else if(enc){
                    if((n = write(nsfd, "E", 1)) < 0){              //send encountered
                        error("ERROR writing to socket: Encountered");
                    }
                    if(!pathflag){
                        printf("Encountered: %d. Sending path ranking...\n", clr_temp);
                        int temp;
                        pthread_mutex_lock(&mtx);
                            temp = color_list[loc][1];
                        pthread_mutex_unlock(&mtx);
                        sprintf(ptr, "%d", temp);
                        if((n = write(nsfd, ptr, 1)) < 0){
                            error("ERROR writing to socket: Path Ranking");
                        }
                        bzero(ptr, strlen(ptr));
                    }else{                                          //If good path is found
                        if((n = write(nsfd, "1", 1)) < 0){
                            error("ERROR writing to socket: Best Path Ranking");
                        }
                        sleep(2);                                   //pause for 2 seconds
                        printf("BEST PATH: %d\n", pathflag);
                        sprintf(ptr, "%d", pathflag);
                        if((n = write(nsfd, ptr, strlen(ptr))) < 0){
                            error("ERROR writing to socket: Best Path");
                        }
                        bzero(ptr, strlen(ptr));
                    }

                    enc = 0;
                }
            }
        }

}

