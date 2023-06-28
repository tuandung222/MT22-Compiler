    .text
    .globl printInteger, printBoolean, printString, printFloat
    
printInteger:
    li  $v0, 1
    syscall
    j END

printBoolean:
    li $v0, 1
    syscall
    j END

printString:
    li $v0, 4
    syscall
    j END

printFloat:
    li $v0, 2
    syscall
    j END

END:
