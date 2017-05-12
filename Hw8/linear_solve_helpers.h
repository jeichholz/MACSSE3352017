
typedef struct{
  double** data;
  int m;
  int n;
}matrix;

typedef struct{
  char* A_file;
  char* b_file;
  char* x_file;
  int produce_output_file;
  int print_results;
}options;


void print_matrix(matrix* A){
  int i,j;
  for (i=0;i<A->m;i++){
    printf("|");
    for (j=0;j<A->n;j++){
      printf("%.3lf",A->data[i][j]);
      if (j<A->n-1){
	printf(" ");
      }
    }
    printf("|\n");
  }
}

void print_usage(){
  printf("linear_solve -- solve a linear system of equations Ax=b\n");
  printf("usage:\n");
  printf("linear_solve <options>\n");
  printf("options:\n");
  printf("A=<filename>     read the matrix A from <filename>. Defaults to A.txt\n");
  printf("b=<filename>     read the vector b from <filename>. Defaults to b.txt\n");
  printf("x=<filename>     if the solution x is being written to file, the filename.\n");
  printf("--produce_file   forces us to write the solution x to a file.\n");
  printf("--print_results=<0|1> determines whether or not x is printed to screen.  Defaults to 1.\n");

}


void print_options(options* o){
  printf("A: %s\n",o->A_file);
  printf("b: %s\n",o->b_file);
  printf("x: %s\n",o->x_file);
  printf("produce x file: %s\n",o->produce_output_file?"YES":"NO");
  printf("print x: %s\n",o->print_results?"YES":"NO");
}


void parse_options(int argc,char** argv, options* o){
  int i;
  o->A_file=malloc(1000*sizeof(char));
  strcpy(o->A_file,"A.txt");
  o->b_file=malloc(1000*sizeof(char));
  strcpy(o->b_file,"b.txt");
  o->x_file=malloc(1000*sizeof(char));
  strcpy(o->x_file,"x.txt");
  o->produce_output_file=0;
  o->print_results=1;

  char* dummys=malloc(1000*sizeof(char));
  int dummyi;
  for (i=1;i<argc;i++){
    if (sscanf(argv[i],"A=%s",dummys)==1){
      strcpy(o->A_file,dummys);
    }
    else if (sscanf(argv[i],"b=%s",dummys)==1){
      strcpy(o->b_file,dummys);
    }
    else if (sscanf(argv[i],"x=%s",dummys)==1){
      strcpy(o->x_file,dummys);
    }
    else if (strcmp(argv[i],"--produce_file")==0){
      o->produce_output_file=1;
    }
    else if (sscanf(argv[i],"--print_results=%d",&dummyi)==1){
      o->print_results=dummyi;
    }
    else{
      fprintf(stderr,"Error, option %s not recognized\n",argv[i]);
      print_usage();
      exit(1);
    }
      
    
  }

}

void init_empty_matrix(matrix* A, int m, int n){
  int i;
  A->m=m; A->n=n;
  A->data=malloc(m*sizeof(double*));
  double* D=calloc(m*n,sizeof(double));
  for (i=0;i<m;i++){
    A->data[i]=D+i*n;
  }
  
}

void load_matrix(char* filename, matrix* A){

  FILE* f=fopen(filename,"r");
  if (f==NULL){
    fprintf(stderr,"Error opening %s for reading.\n",filename);
    exit(1);
  }

  int m,n;
  if (fscanf(f,"%d,%d",&m,&n)!=2){
    fprintf(stderr,"Error reading line 0 of %s, expected matrix dimensions\n",filename);
    exit(1);
  }

  init_empty_matrix(A,m,n);

  int i,j;
  for (i=0;i<m;i++){
    for (j=0;j<n;j++){
      if (fscanf(f,"%lf",&(A->data[i][j]))!=1){
      	fprintf(stderr,"Error reading entry %d,%d of %s\n",i,j,filename);
      	exit(1);
      }
    }
  }
  


}

void write_matrix(char* filename, matrix* A){
  FILE* f=fopen(filename,"w");
  if (f==NULL){
    fprintf(stderr,"Error opening %s for write.\n",filename);
    exit(1);
  }
  int i;
  int j;
  fprintf(f,"%d,%d\n",A->m,A->n);
  for (i=0;i<A->m;i++){
    for (j=0;j<A->n;j++){
      fprintf(f,"%lf ",A->data[i][j]);
    }
    fprintf(f,"\n");
  }
  fclose(f);
}

void print_int_arr(int* A,int l){
  printf("[");
  int i;
  for (i=0;i<l;i++){
    printf("%d,",A[i]);
  }
  printf("]\n");
}


matrix* rand_mat(int m, int n){
  srand(0);
  matrix* A=malloc(sizeof(matrix));
  init_empty_matrix(A,m,n);
  int i,j;
  for (i=0;i<m;i++){
    for (j=0;j<n;j++){
      A->data[i][j]=1.0*(rand()%100);
    }
  }
  return A;
}


matrix* rand_inv_mat(int n){
  int i,j,k;
  matrix* A=rand_mat(n,n);
  matrix* AAT=malloc(sizeof(matrix));
  init_empty_matrix(AAT,n,n);
  for (i=0;i<n;i++){
    for (j=0;j<n;j++){
      for (k=0;k<n;k++){
	AAT->data[i][j]+=A->data[i][k]*A->data[j][k];
      }
    }
  }

  return AAT;

}

double ABS(double a){
  if (a<0){
    return -a;
  }
  else{
    return a;
  }

}

double residual(matrix* A, matrix* x, matrix* b){

  double total=0;
  double tmp=0;
  int i,j;

  for (i=0;i<A->m;i++){
    tmp=0;
    for (j=0;j<A->n;j++){
      tmp+=A->data[i][j]*x->data[j][0];
    }
    total+=ABS(b->data[i][0]-tmp);
  }

  return total;
}
