ENTRY(_start)
SECTIONS {
    .blob . : {
        *(.text.start*)
        *(.text*)
        *(.data*)
        *(.bss*)
        *(.rodata*)
    }

    .shstrtab : {
        *(.shstrtab)
    }

    /DISCARD/ : {
        *(*)
    }
}
