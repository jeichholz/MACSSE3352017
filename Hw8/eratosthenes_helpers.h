#include<string.h>
#include<mpi.h>

typedef struct{
  int n;
  int produce_outputfile;
  char* output_filename;
  int print_results;
}options;

void print_usage(){
  printf("Usage:\neratosthenes <n> <options>\nn -- Find the first n primes n\n");
  printf("\n");
  printf("options:\n");
  printf("n                          -- find the first n prime numbers. Defaults to 100\n");
  printf("--produce_file=<0|1>       -- whether or not to produce a file containing the list of prime numbers found. Defaults to 0.\n");
  printf("--output_file=<filename>   -- if generating a file, the name of the file.  Defaults to primelist.txt\n");
  printf("--print_results=<0|>       -- whether or not to display the list of primes on the terminal. Defaults to 1 if n<= 100, and 0 otherwise\n");
}

void get_opts(int argc, char** argv, options* opts){

  int i;
  int dummyd;
  char dummys[1000];
  opts->n=100;
  opts->produce_outputfile=0;
  opts->output_filename=malloc(1000*sizeof(char));
  opts->print_results=2;
  strcpy(opts->output_filename,"primelist.txt");
  for (i=1;i<argc;i++){
    if (sscanf(argv[i],"%d",&dummyd)==1){
	opts->n=dummyd;
    }
    else if (sscanf(argv[i],"--output_file=%s",dummys)==1){
      opts->produce_outputfile=1;
      strcpy(opts->output_filename,dummys);
    }
    else if (sscanf(argv[i],"--produce_file=%d",&dummyd)==1){
      opts->produce_outputfile=dummyd;
    }
    else if (sscanf(argv[i],"--print_results=%d",&dummyd)==1){
      opts->print_results=dummyd;
    }
    else{
      fprintf(stderr,"Unrecognized option: %s\n", argv[i]);
      print_usage();
      exit(1);
    }
  }
  if (opts->print_results==2){
    opts->print_results= opts->n>100?0:1;
  }

}


void print_options(options* opts){
  printf("N: %d\n",opts->n);
  int size;
  MPI_Comm_size(MPI_COMM_WORLD,&size);
  printf("num processors: %d\n",size);
  printf("produce an output file: %s\n",opts->produce_outputfile ? "YES":"NO");
  printf("output file name: %s\n",opts->output_filename);
  printf("print list: %s\n",opts->print_results ? "YES":"NO");
}


void write_results(long long int primes[], long long int primes_len,options* opts){
  FILE* f=fopen(opts->output_filename,"w");
  if (f==NULL){
    fprintf(stderr,"Error opening file %s for writing\n", opts->output_filename);
    exit(1);
  }

  long long int i;
  for (i=0;i<primes_len;i++){

    fprintf(f,"%lld\n",primes[i]);
  }
  fclose(f);

}
