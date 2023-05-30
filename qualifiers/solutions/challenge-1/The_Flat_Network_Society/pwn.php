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
$p  = popen("./rand", "r");

printf("[+] Done in %f seconds\n", microtime(true) - $time);
printf("\n");

expectLine($fp, "Reticulating splines... ");
$l = fgets($fp);
$r = (strlen($l) - 1) >> 1;
var_dump($r);

// Discard randoms
for($i = 0; $i < $r; $i++)
	fgets($p);

expectLine($fp, "");
expectLine($fp, "Welcome to the maze!");
expectLine($fp, "You are in room (1, 1)");
fgets($fp);
expectLine($fp, "Which would you like to do?");

fwrite($fp, "a\n");
fgets($fp);
expectLine($fp, "You cast arcane eye and send your summoned magical eye above the maze.");

$map = [];
for($i = 0; $i < 0x1e; $i++) {
	$line = line($fp);
	assert(0x1e === strlen($line));
	$map[$i] = $line;
}

function solve($map, $pos, $path)
{
	[$x, $y] = $pos;

	if('#' === $map[$x][$y])
		return false;

	if('*' === $map[$x][$y])
		return $path;

	$map[$x][$y] = '#';

	$ret = false;
	do {
		$ret = solve($map, [$x - 1, $y], $path . "n");
		if($ret) break;

		$ret = solve($map, [$x + 1, $y], $path . "s");
		if($ret) break;

		$ret = solve($map, [$x, $y - 1], $path . "w");
		if($ret) break;

		$ret = solve($map, [$x, $y + 1], $path . "e");
		if($ret) break;
	} while(false);

	$map[$x][$y] = '.';

	return $ret;
}

$path = solve($map, [1, 1], "");

for($i = 0; $i < strlen($path) + 1; $i++)
	fgets($p);

do {
	$n = (int)fgets($p);
	$n %= 0x4BD;
	$path = "n$path";
} while($n !== 0x4BC);

fclose($p);

foreach(str_split($path) as $c)
	fwrite($fp, "$c\n");

fwrite($fp, "exec ./submitter\n");
fwrite($fp, str_repeat("q\n", 0x1000));

while($line = fgets($fp))
	if(false !== strpos($line, "LiveCTF"))
		echo $line;
