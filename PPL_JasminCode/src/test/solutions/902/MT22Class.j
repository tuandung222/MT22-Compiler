.source MT22Class.java
.class public MT22Class
.super java.lang.Object
.field static a I
.field static b I
.field static c [I
.field static m I

.method public static main([Ljava/lang/String;)V
.var 0 is args [Ljava/lang/String; from Label0 to Label1
Label0:
	iconst_1
	putstatic MT22Class/m I
	iconst_3
	newarray int
	dup
	iconst_0
	iconst_1
	iastore
	dup
	iconst_1
	iconst_2
	iastore
	dup
	iconst_2
	iconst_3
	iastore
	putstatic MT22Class/c [I
	iconst_3
	putstatic MT22Class/b I
	iconst_1
	putstatic MT22Class/a I
	iconst_1
	putstatic MT22Class/a I
	getstatic MT22Class/a I
	sipush 2000
	if_icmpge Label2
	iconst_1
	goto Label3
Label2:
	iconst_0
Label3:
	ifle Label4
Label5:
Label6:
Label4:
Label7:
	iconst_1
	ifle Label8
Label9:
	getstatic MT22Class/a I
	iconst_2
	imul
	putstatic MT22Class/a I
	getstatic MT22Class/a I
	sipush 2000
	if_icmpge Label11
	iconst_1
	goto Label12
Label11:
	iconst_0
Label12:
	ifle Label13
Label15:
Label16:
	goto Label14
Label13:
	goto Label8
Label14:
Label10:
	goto Label7
Label8:
	putstatic MT22Class/c [I
	iconst_0
	iaload
	invokestatic io/printInteger(I)V
Label1:
	return
.limit stack 7
.limit locals 1
.end method

.method public static fibo(I)I
Label0:
.var 0 is n I from Label0 to Label1
	iconst_0
	istore_0
	iload_0
	iconst_1
	if_icmpgt Label2
	iconst_1
	goto Label3
Label2:
	iconst_0
Label3:
	ifle Label4
	iload_0
	goto Label1
	goto Label5
Label4:
	iload_0
	iconst_1
	isub
	invokestatic MT22Class/fibo(I)I
	iload_0
	iconst_2
	isub
	invokestatic MT22Class/fibo(I)I
	iadd
	goto Label1
Label5:
Label1:
	ireturn
.limit stack 6
.limit locals 1
.end method

.method public static fibo2(I)I
Label0:
.var 0 is p I from Label0 to Label1
.var 1 is n I from Label0 to Label1
	iload_0
	invokestatic MT22Class/fibo(I)I
	bipush 10
	istore_1
	iload_1
	iconst_1
	if_icmpgt Label2
	iconst_1
	goto Label3
Label2:
	iconst_0
Label3:
	ifle Label4
	iload_1
	goto Label1
	goto Label5
Label4:
	iload_1
	iconst_1
	isub
	invokestatic MT22Class/fibo(I)I
	iload_1
	iconst_2
	isub
	invokestatic MT22Class/fibo(I)I
	iadd
	goto Label1
Label5:
Label1:
	ireturn
.limit stack 6
.limit locals 2
.end method

.method public <init>()V
.var 0 is this LMT22Class; from Label0 to Label1
Label0:
	aload_0
	invokespecial java/lang/Object/<init>()V
Label1:
	return
.limit stack 1
.limit locals 1
.end method
