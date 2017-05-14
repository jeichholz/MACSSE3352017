#include <string.h>
#include <mpi.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int __real_MPI_Send(const void *buf, int count, MPI_Datatype datatype, int dest,
		     int tag, MPI_Comm comm);

int __real_MPI_Init(int* argc, char*** argv);

int __real_MPI_Finalize();

int send_count=0;
int capacity=0;
int deep_log=0;
int* send_partners=NULL;
int* send_data=NULL;
int* send_size=NULL;

int __wrap_MPI_Send(int *buf, int count, MPI_Datatype datatype, int dest,
		     int tag, MPI_Comm comm){

  if (deep_log){
    if (capacity==send_count){
      send_partners=realloc(send_partners,(2*capacity+1000)*sizeof(int));
      send_data=realloc(send_data,(2*capacity+1000)*sizeof(int));
      send_size=realloc(send_size,(2*capacity+1000)*sizeof(int));
      capacity=capacity*2+1000;
    }
     send_partners[send_count]=dest;
     if (buf != NULL){
       send_data[send_count]=((int*)buf)[0];
     }
     else{
       send_data[send_count]=-999;
     }
     send_size[send_count]=count; 
     send_count++; 
  }

  return __real_MPI_Send(buf,count,datatype,dest,tag,comm);
}



int __wrap_MPI_Init(int* argc, char*** argv){
  int s= __real_MPI_Init(argc,argv);

  int i;
  int old_argc=*argc;
  char** old_argv=*argv;
  char** new_argv=malloc(sizeof(char*)*old_argc);
  int new_argc=0;
  for (i=0;i<*argc;i++){
    if (strcmp(old_argv[i],"--deep-log")==0){
      deep_log=1;
    }
    else{
      new_argv[new_argc]=malloc(strlen(old_argv[i])*sizeof(char));
      strcpy(new_argv[new_argc],old_argv[i]);
      new_argc++;
    }
  }

  *argc=new_argc;
  *argv=new_argv;
  return s;
}


int __wrap_MPI_Finalize(){

  if (deep_log){
    char filename[1000];
    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD,&rank);
    sprintf(filename,"whatidid.rank.%d.txt",rank);
    FILE* f= fopen(filename,"w");

    int i;
    for (i=0;i<send_count;i++){
      fprintf(f,"%d: %d %d %d\n",i,send_partners[i],send_data[i],send_size[i]);
    }
    fclose(f);

  }

  return __real_MPI_Finalize();

}
