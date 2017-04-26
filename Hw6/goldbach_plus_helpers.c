
typedef struct{
  long long int p;
  int chunksize;
}options;


void print_usage(FILE* f){
  int rank;
  MPI_Comm_rank(MPI_COMM_WORLD,&rank);
  if (rank==0){
    fprintf(f,"A program for calculating N(p), as described in Hw6.pdf\n");
    fprintf(f, "\n\n");
    fprintf(f, "Options:\n");
    fprintf(f, "--p=<p>             the value of p for which N(p) should be calculated.  Defaults to 10\n");
    fprintf(f, "--chunksize=<size>  the chunksize for dynamic work allocation\n");
    fprintf(f, "-h, --help, ?       print this message\n");
  }
}

void print_options(options* op){
  printf("Finding smallest integer n such that M(n)>=%lld\n",op->p); 
}


void parse_options(int argc, char** argv, options* op){

  op->p=10;
  op->chunksize=50;
  
  int i;
  int dummyi;
  double dummyd1;
  for (i=1;i<argc;i++){
    if (sscanf(argv[i],"--p=%lf",&dummyd1)==1){
      op->p=(long long int)dummyd1;
    }
    else if (sscanf(argv[i],"--chunksize=%d",&dummyi)==1){
      op->chunksize=dummyi;
    }
    else if (strcmp("-h",argv[i])==0 || strcmp("?", argv[i])==0 || strcmp("--help",argv[i])==0){
      print_usage(stdout);
      MPI_Finalize();
      exit(0);
    }
    else{
      printf("Unknown option %s\n",argv[i]);
      print_usage(stderr);
      MPI_Finalize();
      exit(0);
    }
  }

}
