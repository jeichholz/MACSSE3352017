#include <mpi.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "linear_solve_helpers.h"

#define MAX(a,b) (a)>(b)?(a):(b)
#define MIN(a,b) (a)<(b)?(a):(b)



int main(int argc, char** argv){
  MPI_Init(&argc,&argv);
  int rank;
  int size;
  MPI_Comm_size(MPI_COMM_WORLD,&size);
  MPI_Comm_rank(MPI_COMM_WORLD,&rank);

  options o;
  parse_options(argc,argv,&o);

  if (rank==0){
    print_options(&o);
  }

  int Adims[2];
  int top[size];
  int bottom[size];

  matrix localA;
  matrix localb;
  matrix A;
  matrix b;
  if (rank==0){

    load_matrix(o.A_file,&A);
    //print_matrix(&A);
    load_matrix(o.b_file,&b);
    //print_matrix(&b);
    if (b.n!=1){
      fprintf(stderr,"Error, b must be a vector\n");
      exit(1);
    }
    if (A.m!=b.m){
      fprintf(stderr,"Error, A and b must have same number of rows.\n");
      exit(1);
    }

    if (A.m!=A.n){
      fprintf(stderr,"Error, A must be square.\n");
      exit(1);
    }
    //root has now read A and b in, and made sure the dimensions are compatible.
    //Need to distribute A and b appropriately, and then carry on. 
  }
  else{
    //get your chunk of A and b

  }


  //Everyone must take part in the solve


  
  //Do appropriate stuff at the end. 
  if (rank==0){
    if (o.print_results){
      print_matrix(&FinalX);
    }
    printf("Residual is %lf\n",residual(&A,&FinalX,&b));
    if (o.produce_output_file){
      write_matrix(o.x_file,&FinalX);
    }
  }
  
  MPI_Finalize();
  return (0);
}
