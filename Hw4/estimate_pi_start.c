#include<stdio.h>
#include<stdlib.h>
#include<mpi.h>
#include<time.h>
#include<math.h>
#include<unistd.h>

int incircle_calls=0;

int in_circle(double x, double y){
  incircle_calls++;
  return x*x+y*y<1 ? 1 : 0;
}  

int main(int argc, char** argv){
  MPI_Init(&argc,&argv);

  int rank;
  int numprocs;
  int i;
  MPI_Comm_size(MPI_COMM_WORLD,&numprocs);
  MPI_Comm_rank(MPI_COMM_WORLD,&rank);

  if (argc<2){
    if (rank==0){
      printf("Usage: %s T\n",argv[0]);
      printf("where T is the number of trials on each processor.\n");
    }
    MPI_Finalize();
    return(MPI_SUCCESS);
  }

  
  MPI_Finalize();
  return(MPI_SUCCESS);
}
