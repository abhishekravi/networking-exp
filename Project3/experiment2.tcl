set ns [new Simulator]

set var1 [lindex $argv 0]
set var2 [lindex $argv 1]
set rate [lindex $argv 2]
set tcp1_stime [lindex $argv 3]
set tcp2_stime [lindex $argv 4]

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

#setup the topology
$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n5 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
$ns duplex-link $n3 $n4 10Mb 10ms DropTail
$ns duplex-link $n3 $n6 10Mb 10ms DropTail

#Setting UDP between n2 and n3
set udp [new Agent/UDP]
$ns attach-agent $n2 $udp
set null [new Agent/Null]
$ns attach-agent $n3 $null
$ns connect $udp $null
$udp set fid_ 3
set cbr [new Application/Traffic/CBR]
$cbr set type_ CBR
$cbr set packetSize_ 500
$cbr set random_ false
$cbr set rate_ ${rate}mb
$cbr attach-agent $udp

#Setting TCP between n0 and n3
if {$var1 eq "Reno"} {
	set tcp1 [new Agent/TCP/Reno]
} elseif {$var1 eq "NewReno"} {
	set tcp1 [new Agent/TCP/Newreno]
} elseif {$var1 eq "Vegas"} {
	set tcp1 [new Agent/TCP/Vegas]
}
$ns attach-agent $n1 $tcp1
set sink1 [new Agent/TCPSink]
$ns attach-agent $n4 $sink1
$ns connect $tcp1 $sink1
$tcp1 set fid_ 1

#Setting TCP between n4 and n5
if {$var2 eq "Reno"} {
	set tcp2 [new Agent/TCP/Reno]
} elseif {$var2 eq "Vegas"} {
	set tcp2 [new Agent/TCP/Vegas]
}
$ns attach-agent $n5 $tcp2
set sink2 [new Agent/TCPSink]
$ns attach-agent $n6 $sink2
$ns connect $tcp2 $sink2
$tcp2 set fid_ 2

#creating ftp applications
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1
set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2

#setting start and end times
$ns at 5.0 "$cbr start"
$ns at tcp1_stime "$ftp1 start"
$ns at tcp2_stime "$ftp2 start"
$ns at 50.0 "$ftp2 stop"
$ns at 50.0 "$ftp1 stop"
$ns at 50.0 "$cbr stop"

$ns at 51.0 "connection_stop"

$ns run

