for {set i 0} {$i <= 100} {incr i} {
    puts -nonewline "\rProgress: $i%"
    flush stdout
    after 5  ;
}
puts ""  ;