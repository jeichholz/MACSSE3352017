#include<stdio.h>
#include<stdlib.h>
#include<mpi.h>
#include<math.h>
#include<string.h>
#include"bucketsort_helpers.h"

//Takes a list L, of length n, whose elements are evenly distributed between a and b, and classify
//the elements.
//The "buckets", held in B, are arrays.
//There are m buckets, B[0], B[1], ... , B[m-1].
//The buckets must be pre-allocated, the capacity of each bucket is held in bucket_capacity.
//After filling, the number of elements in B[i] is returned in bucket_len[i].

void fill_buckets(double* L, int n, double a, double b, double** B, int m, int bucket_capacity, int* bucket_len){

}



void main(int argc, char** argv){
  
  MPI_Init(&argc,&argv);
  int rank;
  int nproc;
  MPI_Comm_size(MPI_COMM_WORLD,&nproc);
  MPI_Comm_rank(MPI_COMM_WORLD,&rank);

  options opts;


  double* L;     //the list L.  Only the root will ever have a complete copy of this.
  int L_len;
  double* subL;  //the sublist of L that I will sort
  int subL_len;  //The length of that sublist

  double start, end;

  //Every process is good to read the options off the command line, because
  //they all have the command line options, thanks to MPI.
  //Eliminates passing around a bunch of options.


  int i;
  parse_options(argc,argv,&opts);

  //This code gets the master set up with the data, and prints out the initial message. 
  if (rank==0){  
    //rank 0 has the initial list.  Either make it randomly or read it from the input file.
    if (opts.n==-1){
      read_inputfile(opts.inputfile, &L, &opts);
    }
    else{
      //seed the random number generator with 1 everytime to get consistent results. 
      srand(1);
      L=malloc(opts.n*sizeof(double));

      //fill up the list with random stuff
      for (i=0;i<opts.n;i++){
	L[i]=((double)rand())/RAND_MAX*(opts.b-opts.a)+opts.a;
      }
    }

    print_options(&opts);

    printf("Bucket-Sorting %d elements using %d processes.\n",opts.n,opts.nproc);

   //print the initial list if is is nice and small
   if (opts.print_things){
     printf("L: ");
     print_arr(L,opts.n);
   }

  } //Done with that.  Now do some stuff!




  


  //At the end, the master prints out the sorted list if necessary, prints the outputfile, and if requested it checks to make sure that the list really is sorted. 
  if (rank==0){
  write_outputfile(opts.outputfile,L,opts.n);
     
     if (opts.print_things){
       printf("L:");
       print_arr(L,opts.n);
     }
     if (opts.check_results){
       if (is_sorted(L,opts.n)){
	 printf("L is sorted ascending\n");
       }
       else{
	 printf("L is NOT sorted ascending!!!\n");
       }
     }
   }


  MPI_Finalize();

}




