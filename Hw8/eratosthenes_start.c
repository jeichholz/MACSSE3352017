#include<stdio.h>
#include<stdlib.h>
#include "eratosthenes_helpers.h"
#include "math.h"
#include <mpi.h>

//El-clasico, the Seive of Eratosthenes.  Now in parallel!  Coming to a store near you!

int main(int argc, char** argv){
  MPI_Init(&argc,&argv);

  int rank,nproc;
  MPI_Comm_size(MPI_COMM_WORLD,&nproc);
  MPI_Comm_rank(MPI_COMM_WORLD,&rank);

  MPI_Status stat;
  options opts;
  get_opts(argc,argv,&opts);
  if (rank==0){
    print_options(&opts);
  }
  int i;
  //Stuff!

  if (rank==0){
    if (opts.print_results){
      for (i=0;i<opts.n;i++){
	printf("%lld\n",allprimes[i]);
      }
    }

    if (opts.produce_outputfile){
      write_results(allprimes,opts.n,&opts);
    }
  }
  MPI_Finalize();
  
  return(0);
}
