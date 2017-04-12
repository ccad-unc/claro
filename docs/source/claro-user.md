% claro-user(1)

# NAME

claro-user - manages users in a cluster

# SYNOPSIS

    claro user check <username> <hostlist>
    claro user add <username>
    claro user del <username> 
    claro user -h | --help

# DESCRIPTION

*claro ipmi* offers a simplified interface for managing users, roles and permissions
in a cluster.

# OPTIONS

    claro user check <username> <hostlist>

        Check if an user exist in a hostlist


For the commands that allow to interact multiple nodes at the same time,
the <hostlist> can be replaced by the key word "nodes", defined in the 
configuration file in the [common] section.


# EXAMPLES

This command check if user "antonio" exist in all the nodes:

    claro user check antonio nodes

# SEE ALSO

claro(1), claro-ipmi(1)
