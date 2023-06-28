	.text
	.globl main
	li $t0, 9
	move $t1, $t0
	sw $t1, 0($gp)
main:
	subu $sp, $sp, 8
	sw $fp, 8($sp)
	sw $ra, 4($sp)
	addiu $fp, $sp, 8
	li $t1, 30
	move $t2, $t1
	li $t3, 30
	move $t4, $t3
	sw $t2, -12($fp)
	sw $t4, 0($gp)
L0:
	li $t2, 10
	lw $t4 0($gp)
	sgt $t5, $t4, $t2
	beqz $t5, L1
	li $t6, 5
	sub $t7, $t4, $t6
	move $t4, $t7
	sw $t4, 0($gp)
	j L0
L1:
	li $t4, 1
	li $t8, 1
	sub $t9, $t4, $t8
	beqz $t9, L3
	lw $s0 -12($fp)
	move $a0, $s0
	jal printInteger
	j L2
L3:
	li $s1, 1
	move $a0, $s1
	jal foo
	move $s2, $v0
	lw $s3 0($gp)
	add $s4, $s2, $s3
	move $a0, $s4
	jal printInteger
L2:
foo:
	subu $sp, $sp, 8
	sw $fp, 8($sp)
	sw $ra, 4($sp)
	addiu $fp, $sp, 8
	li $s5, 0
	move $s6, $s5
	li $s7, 3
	sub $t0, $s7, $a0
	move $s6, $t0
	move $v0, $s6
	move $sp, $fp
	lw $ra, -4($fp)
	lw $fp, 0($fp)
	jr $ra
