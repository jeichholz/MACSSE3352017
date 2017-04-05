#include<stdio.h>
#include<mpi.h>
#include<stdlib.h>
#include<string.h>

int __real_MPI_Finalize();
int __real_incircle(double,double);
void __real_srand(unsigned int);

int srand_times=0;
int* srand_seeds=NULL;
int logsize=10;
extern int incircle_calls;


void __wrap_srand(unsigned int seed){
  if (srand_seeds==NULL){
    srand_seeds=malloc(logsize*sizeof(unsigned int));
  }
  if (srand_times<logsize){
    srand_seeds[srand_times]=seed;
  }
  srand_times++;
  __real_srand(seed);
}

int __wrap_MPI_Finalize(){
  int rank;
  MPI_Comm_rank(MPI_COMM_WORLD,&rank);
  char filename[20];
  sprintf(filename,"whatidid.rank.%d",rank);
  FILE* f = fopen(filename,"w");
  int i;
  fprintf(f,"Times srand seeded: %d\n",srand_times);
  fprintf(f,"seeds used in srand: ");
  for (i=0;i<srand_times-1;i++){
    fprintf(f,"%d,",srand_seeds[i]);
  }
  if (srand_times>0){
    fprintf(f,"%d\n",srand_seeds[srand_times-1]);
  }
  fprintf(f,"in_circle_calls: %d\n",incircle_calls);
  fclose(f);
  return __real_MPI_Finalize();

}
