set ns [new Simulator]

set varants [lindex $argv 0]
set que_discipl [lindex $argv 1]
set tf [open output.tr w]
$ns trace-all $tf
proc connection_stop {} {
        global ns tf
        $ns flush-trace
        close $tf
        exit 0
}
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

$ns duplex-link $n1 $n2 10Mb 10ms $que_discipl
$ns duplex-link $n2 $n3 10Mb 10ms $que_discipl
$ns duplex-link $n3 $n4 10Mb 10ms $que_discipl
$ns duplex-link $n5 $n2 10Mb 10ms $que_discipl
$ns duplex-link $n3 $n6 10Mb 10ms $que_discipl

#Setting queue size
$ns queue-limit $n1 $n2 5
$ns queue-limit $n2 $n3 5
$ns queue-limit $n3 $n4 5
$ns queue-limit $n5 $n2 5
$ns queue-limit $n3 $n6 5

#Setting UDP between n5 and n6
set udp [new Agent/UDP]
$ns attach-agent $n5 $udp
set null [new Agent/Null]
$ns attach-agent $n6 $null
$ns connect $udp $null
$udp set fid_ 2

#Setting CBR
set cbr [new Application/Traffic/CBR]
$cbr set type_ CBR
$cbr set packetSize_ 500
$cbr set random_ false
$cbr set rate_ 7Mb
$cbr attach-agent $udp

#Setting TCP between n1 and n4
if {$varants eq "Reno"} {
set tcp [new Agent/TCP/Reno]
set sink [new Agent/TCPSink]
} elseif {$varants eq "SACK"} {
set tcp [new Agent/TCP/Sack1]
set sink [new Agent/TCPSink/Sack1]
}

$ns attach-agent $n1 $tcp
$ns attach-agent $n4 $sink
$ns connect $tcp $sink
$tcp set fid_ 1

set ftp [new Application/FTP]
$ftp attach-agent $tcp

$ns at 150.0 "$cbr start"
$ns at 300.0 "$cbr stop"
$ns at 1.0 "$ftp start"
$ns at 300.0 "$ftp stop"

$ns at 300.0 "connection_stop"

$ns run
