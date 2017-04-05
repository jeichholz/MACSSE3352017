ARCH=$(shell uname -p)
OBJS=./objs

CC=mpicc

.PHONY:broadcast_messages_standard
broadcast_messages_standard:
	${CC} -lm ${OBJS}/broadcast_messages_standard.${ARCH}.o -o broadcast_messages_standard


.PHONY:ring_broadcast_standard
ring_broadcast_standard:
	${CC} -lm ${OBJS}/ring_broadcast_standard.${ARCH}.o -o ring_broadcast_standard

.PHONY: comm_speed_standard
comm_speed_standard:
	${CC} -lm ${OBJS}/comm_speed_standard.${ARCH}.o -o comm_speed_standard

.PHONY: estimate_pi_standard
estimate_pi_standard:
	${CC} -lm ${OBJS}/estimate_pi_standard.${ARCH}.o -o estimate_pi_standard

.PHONY: palindromes_standard
palindromes_standard:
	${CC} -lm ${OBJS}/palindromes_standard.${ARCH}.o -o palindromes_standard

.PHONY: all
all: palindromes_standard estimate_pi_standard comm_speed_standard ring_broadcast_standard broadcast_messages_standard

