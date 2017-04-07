% claro-ipmi(1)

# NAME

claro-ipmi - manages and get the status from the nodes of a cluster

# SYNOPSIS

    claro ipmi connect [-jf] <host>
    claro ipmi getmac <hostlist>
    claro ipmi [--p=<level>] deconnect <hostlist>
    claro ipmi [--p=<level>] (on|off|reboot) <hostlist>
    claro ipmi [--p=<level>] status <hostlist>
    claro ipmi [--p=<level>] setpwd <hostlist>
    claro ipmi [--p=<level>] pxe <hostlist>
    claro ipmi [--p=<level>] disk <hostlist>
    claro ipmi [--p=<level>] ping <hostlist>
    claro ipmi [--p=<level>] blink <hostlist>
    claro ipmi [--p=<level>] immdhcp <hostlist>
    claro ipmi [--p=<level>] bios <hostlist>
    claro ipmi [--p=<level>] reset <hostlist>
    claro ipmi [--p=<level>] sellist <hostlist>
    claro ipmi [--p=<level>] selclear <hostlist>
    claro ipmi [--p=<level>] ssh <hostlist> <command>
    claro ipmi -h | --help
Alternative:
    claro ipmi <host> connect [-jf]
    claro ipmi <hostlist> getmac
    claro ipmi [--p=<level>] <hostlist> deconnect
    claro ipmi [--p=<level>] <hostlist> (on|off|reboot)
    claro ipmi [--p=<level>] <hostlist> status
    claro ipmi [--p=<level>] <hostlist> setpwd
    claro ipmi [--p=<level>] <hostlist> pxe
    claro ipmi [--p=<level>] <hostlist> disk
    claro ipmi [--p=<level>] <hostlist> ping
    claro ipmi [--p=<level>] <hostlist> blink
    claro ipmi [--p=<level>] <hostlist> immdhcp
    claro ipmi [--p=<level>] <hostlist> bios
    claro ipmi [--p=<level>] <hostlist> reset
    claro ipmi [--p=<level>] <hostlist> sellist
    claro ipmi [--p=<level>] <hostlist> selclear
    claro ipmi [--p=<level>] <hostlist> ssh <command>

# DESCRIPTION

*claro ipmi* offers a simplified interface of ipmitool, an utility for controlling
IPMI-enabled devices. The username and password needed by ipmitool are handled
automatically.

# OPTIONS

    claro ipmi connect [-jf] <host>

        Connect to IMM serial console, including video, keyboard and mouse controlling
        The flag -j joins the connection and the flag -f forces it.

    claro ipmi deconnect <host>

        Deconnect from a IMM serial console

    claro ipmi on <hostlist>

        Power up chassis

    claro ipmi off <hostlist>

        Power down chassis into soft off. WARNING: it does do a clean shutdown of the OS.

    claro ipmi reboot <hostlist>

        This command will perform a hard reset

    claro ipmi status <hostlist>

        Get target node power status using the IMM device

    claro ipmi setpwd <hostlist>

        Set up IMM user id/password on a new device

    claro ipmi getmac <hostlist>

        Get node MAC addresses using the IMM device

    claro ipmi pxe <hostlist>

        Use IMM to perform a network boot on the next reboot

    claro ipmi disk <hostlist>

        Use IMM to perform a disk boot on the next reboot

    claro ipmi ping <hostlist>

        Use fping to check status of the machines

    claro ipmi blink <hostlist>

        Make chassis blink to help on-site admins to identify the machine

    claro ipmi immdhcp <hostlist>

        Set selected ipmi interfaces to grab an IP via DHCP

    claro ipmi bios <hostlist>

        Make selected machines go directly into BIOS on next reboot

    claro ipmi sellist <hostlist>

        Display the entire content of the System Event Log (SEL).

    claro ipmi selclear <hostlist>

        Clear the contents of the System Event Log (SEL). It cannot be undone so be careful.

    claro ipmi reset <hostlist>

        Reset the IMM device (cold reset)

    claro ipmi ssh <hostlist> <command>

        Run a command through the SSH interface of the IMM

For the commands that allow to interact multiple nodes at the same time,
the command can be run in parallel using [--p=<level>].
The parallelism to use by default can be set in the configuration file
in the [ipmi] section with the paramenter "parallel". This value is overridden
by the input from the command line.

Furthermore, the <hostlist> can be replaced by the key word "nodes", defined 
in the configuration file in the [common] section.


# EXAMPLES

This command will ping all hosts nodes from node12 to n99:

    claro ipmi ping node[12-99]

To check the status from node13:

    claro ipmi status node13

Or also:

    claro ipmi node13 status

And you can check the status of all the nodes using parallelism:

    claro ipmi --p=16 status node[12-99]

# SEE ALSO

claro(1)
