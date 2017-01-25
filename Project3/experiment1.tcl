set ns [new Simulator] 

# Setting different variants and rates 
set var [lindex $argv 0]
set rates [lindex $argv 1]
set udp_stime [lindex $argv 2]
set tcp_stime [lindex $argv 3]
set tf [open output.tr w]

$ns trace-all $tf
proc connection_stop {} {
        global ns tf
        $ns flush-trace
        close $tf
        exit 0
}

#Setting nodes

set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

#Setting connection between nodes

$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
$ns duplex-link $n3 $n4 10Mb 10ms DropTail
$ns duplex-link $n5 $n2 10Mb 10ms DropTail
$ns duplex-link $n3 $n6 10Mb 10ms DropTail

#Setting UDP Connnection between node n2 and n3

set udp [new Agent/UDP]
$ns attach-agent $n2 $udp
set null [new Agent/Null]
$ns attach-agent $n3 $null
$ns connect $udp $null
$udp set fid_ 2
set cbr [new Application/Traffic/CBR]
$cbr set type_ CBR
$cbr set packetSize_ 500
$cbr set random_ false
$cbr set rate_ ${rates}mb
$cbr attach-agent $udp

#setting tcp type from n1 to n4
if {$var eq "Tahoe"} {
	set tcp [new Agent/TCP]
} elseif {$var eq "Reno"} {
	set tcp [new Agent/TCP/Reno]
} elseif {$var eq "NewReno"} {
	set tcp [new Agent/TCP/Newreno]
} elseif {$var eq "Vegas"} {
	set tcp [new Agent/TCP/Vegas]
}
#set tcp [new Agent/TCP/Vegas]
$ns attach-agent $n1 $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink
$tcp set fid_ 1
set ftp [new Application/FTP]
$ftp attach-agent $tcp

#Defining start time and end time 

$ns at ${udp_stime} "$cbr start"
$ns at 50.0 "$cbr stop"
$ns at ${tcp_stime} "$ftp start"
$ns at 50.0 "$ftp stop"

$ns at 50.0 "connection_stop"

$ns run

