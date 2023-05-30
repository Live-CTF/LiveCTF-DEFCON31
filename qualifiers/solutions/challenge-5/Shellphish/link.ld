OUTPUT_FORMAT("elf64-x86-64", "elf64-x86-64",
          "elf64-x86-64")
OUTPUT_ARCH(i386:x86-64)
ENTRY(_start)
SEARCH_DIR("=/usr/local/lib/x86_64-linux-gnu"); SEARCH_DIR("=/lib/x86_64-linux-gnu"); SEARCH_DIR("=/usr/lib/x86_64-linux-gnu"); SEARCH_DIR("=/usr/local/lib64"); SEARCH_DIR("=/lib64"); SEARCH_DIR("=/usr/lib64"); SEARCH_DIR("=/usr/local/lib"); SEARCH_DIR("=/lib"); SEARCH_DIR("=/usr/lib"); SEARCH_DIR("=/usr/x86_64-linux-gnu/lib64"); SEARCH_DIR("=/usr/x86_64-linux-gnu/lib");
TARGET(binary)
INPUT (/home/livectf/.config.toml)
SECTIONS
{
  . = 0x1000000;
  .text : { *(.text) }
  .rodata 0x200000 : { /home/livectf/.config.toml }
  .test 0x200000  (COPY) : { *(.rodata) }
  . = 0x8000000;
  .data : { *(.data) }
  . = 0x4000000;
  .bss : { *(.bss) }
}
