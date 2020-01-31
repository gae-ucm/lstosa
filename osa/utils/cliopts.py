from optparse import OptionParser   # from version 2.3 to 2.7
from argparse import ArgumentParser
from . import standardhandle
from . import options
##############################################################################
#
# closercliparsing
#
##############################################################################
def closer_argparser():
    tag = standardhandle.gettag()
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", action = "store", dest = "configfile", default = None,
                      help = "use specific config file [default cfg/osa.cfg]")
    parser.add_argument("-d", "--date", action = "store", type = str, dest = "date",
                      help = "observation ending date YYYY_MM_DD [default today]")
    parser.add_argument("-n", "--usenightsummary", action = "store_true", dest = "nightsum", default = False,
                      help = "rely on existing nightsumary file")
    parser.add_argument("-o", "--outputdir", action = "store", type = str, dest = "directory",
                      help = "analysis output directory")
    parser.add_argument("-r", "--reason", action = "store", type = str, dest = "reason",
                      choices = ['moon', 'weather', 'other'],
                      help = "reason for closing without data: (moon, weather, other)")
    parser.add_argument("-s", "--simulate", action = "store_true", dest = "simulate", default = False,
                      help = "do not run, just show what would happen")
    parser.add_argument("-y", "--yes", action = "store_true", dest = "noninteractive", default = False,
                      help = "assume yes to all questions")
    parser.add_argument("-v", "--verbose", action = "store_true", dest = "verbose", default = False,
                      help = "make lots of noise for debugging")
    parser.add_argument("-w", "--warnings", action = "store_true", dest = "warning", default = False,
                      help = "show useful warnings")
    parser.add_argument("--stderr", action = "store", type = str, dest = "stderr",
                      help = "file for standard error")
    parser.add_argument("--stdout", action = "store", type = str, dest = "stdout",
                      help = "file for standard output")
    parser.add_argument("--seq", action = "store", type = str, dest = "seqtoclose",
                      help="If you only want to close a certain sequence")
    parser.add_argument('tel_id', choices=['ST', 'LST1', 'LST2'])
    return parser

def closercliparsing():
    tag = standardhandle.gettag()

    # Parse the command line
    opts = closer_argparser().parse_args()

    # Set global variables
    options.configfile = opts.configfile
    options.stderr = opts.stderr
    options.stdout = opts.stdout
    options.date = opts.date
    options.directory = opts.directory
    options.nightsum = opts.nightsum
    options.noninteractive = opts.noninteractive
    options.simulate = opts.simulate
    options.verbose = opts.verbose
    options.warning = opts.warning
    options.reason = opts.reason
    options.seqtoclose = opts.seqtoclose
    options.tel_id = opts.tel_id

    standardhandle.verbose(tag, "the options are {0}".format(opts))

    # Setting the default date and directory if needed
    options.configfile = set_default_configfile_if_needed('closer.py')
    options.date = set_default_date_if_needed()
    options.directory = set_default_directory_if_needed()

    # Setting on the usage of night summary
    options.nightsum = True
##############################################################################
#
# calibrationsequencecliparsing
#
##############################################################################
def calibrationsequencecliparsing(command):
    tag = standardhandle.gettag()
    message = "usage: %prog [-vw] [-c CONFIGFILE] [-d DATE] [-o OUTPUTDIR] [-z] <CAL_RUN_ID> <PED_RUN_ID>  <TEL_ID>"
    parser = OptionParser(usage = message)
    parser.add_option("-c", "--config", action = "store", dest = "configfile", default = None,
                      help = "use specific config file [default cfg/osa.cfg]")
    parser.add_option("-d", "--date", action = "store", type = "string", dest = "date",
                      help = "observation ending date YYYY_MM_DD [default today]")
    parser.add_option("-o", "--outputdir", action = "store", type = "string", dest = "directory",
                      help = "write files to output directory")
    parser.add_option("-v", "--verbose", action = "store_true", dest = "verbose", default = False,
                      help = "make lots of noise for debugging")
    parser.add_option("-w", "--warnings", action = "store_true", dest = "warning", default = False,
                      help = "show useful warnings")
    parser.add_option("-z", "--rawzip", action = "store_true", dest = "compressed", default = False,
                      help = "Use input as compressed raw.gz files")
    parser.add_option("--stderr", action = "store", type = "string", dest = "stderr",
                      help = "file for standard error")
    parser.add_option("--stdout", action = "store", type = "string", dest = "stdout",
                      help = "file for standard output")

    # Parse the command line
    (opts, args) = parser.parse_args()

    # Set global variables
    options.configfile = opts.configfile
    options.stderr = opts.stderr
    options.stdout = opts.stdout
    options.date = opts.date
    options.directory = opts.directory
    options.verbose = opts.verbose
    options.warning = opts.warning
    options.compressed = opts.compressed

    # The standardhandle has to be declared here, since verbose and warnings are options from the cli
    standardhandle.verbose(tag, "the options are {0}".format(opts))
    standardhandle.verbose(tag, "the argument is {0}".format(args))

    # Mapping the telescope argument to an option parameter (it might become an option in the future)
    if len(args) != 3:
        standardhandle.error(tag, "incorrect number of arguments, type -h for help", 2)
    elif args[1] == 'ST':
        standardhandle.error(tag, "not yet ready for telescope {0}".format(options.options.tel_id), 2)
    elif args[1] != 'LST1' and args[1] != 'LST2':
        standardhandle.error(tag, "wrong telescope id, use 'LST1', 'LST2' or 'ST'", 2)

    options.tel_id = args[1]

    # Setting the default date and directory if needed
    options.configfile = set_default_configfile_if_needed(command)
    options.date = set_default_date_if_needed()
    options.directory = set_default_directory_if_needed()

    return args
##############################################################################
#
# datasequencecliparsing
#
##############################################################################
def datasequencecliparsing(command):
    tag = standardhandle.gettag()
    message = "usage: %prog  [-vw] [--stderr=FILE] [--stdout=FILE] [-c CONFIGFILE] [-d DATE] [-o OUTPUTDIR] [-z] <calibrationfile> <pedestalfile> <drivefile> <timecalibration> <RUN> <TEL_ID>"
    parser = OptionParser(usage = message)
    parser.add_option("-c", "--config", action = "store", dest = "configfile", default = None,
                      help = "use specific config file [default cfg/osa.cfg]")
    parser.add_option("-d", "--date", action = "store", type = "string", dest = "date",
                      help = "observation ending date YYYY_MM_DD [default today]")
    parser.add_option("-o", "--outputdir", action = "store", type = "string", dest = "directory",
                          help = "analysis output directory")
    parser.add_option("-v", "--verbose", action = "store_true", dest = "verbose", default = False,
                      help = "make lots of noise for debugging")
    parser.add_option("-w", "--warnings", action = "store_true", dest = "warning", default = False,
                      help = "show useful warnings")
    parser.add_option("-z", "--rawzip", action = "store_true", dest = "compressed", default = False,
                      help = "Use input as compressed raw.gz files")
    parser.add_option("--stderr", action = "store", type = "string", dest = "stderr",
                      help = "file for standard error")
    parser.add_option("--stdout", action = "store", type = "string", dest = "stdout",
                      help = "file for standard output")

    # Parse the command line
    (opts, args) = parser.parse_args()

    # Set global variables
    options.configfile = opts.configfile
    options.stderr = opts.stderr
    options.stdout = opts.stdout    
    options.date = opts.date
    options.directory = opts.directory
    options.verbose = opts.verbose
    options.warning = opts.warning
    options.compressed = opts.compressed

    # The standardhandle has to be declared here, since verbose and warnings are options from the cli
    standardhandle.verbose(tag, "the options are {0}".format(opts))
    standardhandle.verbose(tag, "the argument is {0}".format(args))

    # Checking arguments
    if len(args) != 6:
        standardhandle.error(tag, "incorrect number of arguments, type -h for help", 2)
    # Mapping the telescope argument to an option parameter (it might become an option in the future)
    elif args[5] == 'ST':
        standardhandle.error(tag, "not yet ready for telescope {0}".format(options.options.tel_id), 2)
    elif args[5] != 'LST1' and args[5] != 'LST2':
        standardhandle.error(tag, "wrong telescope id, use 'LST1', 'LST2' or 'ST'", 2)
    options.tel_id = args[5]

    # Setting the default date and directory if needed
    options.configfile = set_default_configfile_if_needed(command)
    options.date = set_default_date_if_needed()
    options.directory = set_default_directory_if_needed()

    return args
##############################################################################
#
# stereosequencecliparsing
#
##############################################################################
def stereosequencecliparsing(command):
    tag = standardhandle.gettag()
    message = "usage: %prog  [-vw] [--stderr=FILE] [--stdout=FILE] [-c CONFIGFILE] [-d DATE] [-o OUTPUTDIR] [-z] <RUN>"
    parser = OptionParser(usage = message)
    parser.add_option("-c", "--config", action = "store", dest = "configfile", default = None,
                      help = "use specific config file [default cfg/osa.cfg]")
    parser.add_option("-d", "--date", action = "store", type = "string", dest = "date",
                      help = "observation ending date YYYY_MM_DD [default today]")
    parser.add_option("-o", "--outputdir", action = "store", type = "string", dest = "directory",
                          help = "analysis output directory")
    parser.add_option("-v", "--verbose", action = "store_true", dest = "verbose", default = False,
                      help = "make lots of noise for debugging")
    parser.add_option("-w", "--warnings", action = "store_true", dest = "warning", default = False,
                      help = "show useful warnings")
    parser.add_option("-z", "--rawzip", action = "store_true", dest = "compressed", default = False,
                      help = "Use input as compressed raw.gz files")
    parser.add_option("--stderr", action = "store", type = "string", dest = "stderr",
                      help = "file for standard error")
    parser.add_option("--stdout", action = "store", type = "string", dest = "stdout",
                      help = "file for standard output")

    # Parse the command line
    (opts, args) = parser.parse_args()

    # Set global variables
    options.configfile = opts.configfile
    options.stderr = opts.stderr
    options.stdout = opts.stdout    
    options.date = opts.date
    options.directory = opts.directory
    options.verbose = opts.verbose
    options.warning = opts.warning
    options.compressed = opts.compressed

    # The standardhandle has to be declared here, since verbose and warnings are options from the cli
    standardhandle.verbose(tag, "the options are {0}".format(opts))
    standardhandle.verbose(tag, "the argument is {0}".format(args))

    # Checking arguments
    if len(args) != 1:
        standardhandle.error(tag, "incorrect number of arguments, type -h for help", 2)
    # Mapping the telescope argument to an option parameter (it might become an option in the future)
    options.tel_id = 'ST'

    # Setting the default date and directory if needed
    options.configfile = set_default_configfile_if_needed(command)
    options.date = set_default_date_if_needed()
    options.directory = set_default_directory_if_needed()

    return args
##############################################################################
#
# sequencercliparsing
#
##############################################################################
def sequencer_argparser():
    tag = standardhandle.gettag()
    parser = ArgumentParser()
    """ Options which define variables """
    parser.add_argument("-c", "--config", action = "store", dest = "configfile", default = None,
                        help = "use specific config file [default cfg/osa.cfg]")
    parser.add_argument("-d", "--date", action = "store", type = str, dest = "date",
                        help = "observation ending date YYYY_MM_DD [default today]")
    parser.add_argument("-m", "--mode", action = "store", type = str, dest = "mode", choices = ['P', 'S', 'T'],
                        help = "mode to run dependant sequences:\n P=parallel [default], S=Sequential, T=temperature-aware")
    """ Boolean options """
    parser.add_argument("-n", "--usenightsummary", action = "store_true", dest = "nightsum", default = False,
                        help = "rely on existing nightsumary file")
    parser.add_argument("-o", "--outputdir", action = "store", type = str, dest = "directory",
                        help = "analysis output directory")
    parser.add_argument("-s", "--simulate", action = "store_true", dest = "simulate", default = False,
                        help = "do not submit sequences as jobs")
    parser.add_argument("-v", "--verbose", action = "store_true", dest = "verbose", default = False,
                        help = "make lots of noise for debugging")
    parser.add_argument("-w", "--warnings", action = "store_true", dest = "warning", default = False,
                        help = "show useful warnings")
    parser.add_argument("-z", "--rawzip", action = "store_true", dest = "compressed", default = False,
                        help = "Use input as compressed raw.gz files, compulsory if using -n and raw.gz files")
    parser.add_argument("--stderr", action = "store", type = str, dest = "stderr",
                        help = "file for standard error")
    parser.add_argument("--stdout", action = "store", type = str, dest = "stdout",
                        help = "file for standard output")
    parser.add_argument('tel_id', choices=['ST', 'LST1', 'LST2', 'all'], help = "telescope identifier LST1, LST2, ST or all.")
    return parser

def sequencercliparsing(command):
    tag = standardhandle.gettag()

    # Parse the command line
    opts = sequencer_argparser().parse_args()

    # Set global variables
    options.configfile = opts.configfile
    options.stderr = opts.stderr
    options.stdout = opts.stdout
    options.date = opts.date
    options.directory = opts.directory
    options.mode = opts.mode
    options.nightsum = opts.nightsum
    options.simulate = opts.simulate
    options.verbose = opts.verbose
    options.warning = opts.warning
    options.compressed = opts.compressed
    options.tel_id = opts.tel_id

    # The standardhandle has to be declared before here, since verbose and warnings are options from the cli
    standardhandle.verbose(tag, "the options are {0}".format(opts))

    # Set the default value for mode
    if not opts.mode:
        options.mode = 'P'

    # Setting the default date and directory if needed
    options.configfile = set_default_configfile_if_needed('sequencer.py')
    options.date = set_default_date_if_needed()
##############################################################################
#
# monolithcliparsing
#
##############################################################################
def monolithcliparsing(command):
    tag = standardhandle.gettag()
    message = "usage: %prog [-syvw] [--stderr=FILE] [--stdout=FILE] [-c CONFIGFILE] [-t] TEL_ID"
    parser = OptionParser(usage = message)
    # Options which define variables
    parser = OptionParser(usage = message)
    parser.add_option("-c", "--config", action = "store", dest = "configfile", default = None,
                      help = "use specific config file [default cfg/osa.cfg]")
    parser.add_option("-t", "--telescope", action = "store", type = "choice", dest = "tel_id",
                      choices = ['LST1', 'LST2', 'ST'], help = "telescope identifier LST1, LST2 or ST [default all]")
    parser.add_option("-s", "--simulate", action = "store_true", dest = "simulate", default = False,
                      help = "do not run, just show what would happen")
    parser.add_option("-y", "--yes", action = "store_true", dest = "noninteractive", default = False,
                      help = "assume yes to all questions")
    parser.add_option("-v", "--verbose", action = "store_true", dest = "verbose", default = False,
                      help = "make lots of noise for debugging")
    parser.add_option("-w", "--warnings", action = "store_true", dest = "warning", default = False,
                      help = "show useful warnings")
    parser.add_option("--stderr", action = "store", type = "string", dest = "stderr",
                      help = "file for standard error")
    parser.add_option("--stdout", action = "store", type = "string", dest = "stdout",
                      help = "file for standard output")

    # Parse the command line
    (opts, args) = parser.parse_args()

    # Set global variables
    options.configfile = opts.configfile
    options.stderr = opts.stderr
    options.stdout = opts.stdout    
    options.tel_id = opts.tel_id
    options.simulate = opts.simulate
    options.noninteractive = opts.noninteractive
    options.verbose = opts.verbose
    options.warning = opts.warning

    # The standardhandle has to be declared here, since verbose and warnings are options from the cli
    standardhandle.verbose(tag, "the options are {0}".format(opts))
    standardhandle.verbose(tag, "the argument is {0}".format(args))

    # Mapping the telescope argument to an option parameter (it might become an option in the future)
    if len(args) > 1:
        standardhandle.error(tag, "incorrect number of arguments, type -h for help", 2)
    elif len(args) == 1:
        if (args[0] != 'LST1' and args[0] != 'LST2' and args[0] != 'ST'):
            standardhandle.error(tag, "wrong telescope id, use 'LST1', 'LST2' or 'ST'", 2)
        options.tel_id = args[0]

    options.configfile = set_default_configfile_if_needed(command)
    return args
##############################################################################
#
# rawcopycliparsing
#
##############################################################################
def rawcopycliparsing(command):
    tag = standardhandle.gettag()
    message = "usage: %prog [-vw] [--stderr=FILE] [--stdout=FILE] [-c CONFIGFILE] [-d DATE] [-z] <TEL_ID>"
    parser = OptionParser(usage = message)
    parser.add_option("-c", "--config", action = "store", dest = "configfile", default = None,
                      help = "use specific config file [default rawcopy.cfg]")
    parser.add_option("-d", "--date", action = "store", type = "string", dest = "date",
                      help = "observation ending date YYYY_MM_DD [default today]")
    parser.add_option("--nocheck", action = "store_true", dest = "nocheck", default = False,
                          help = "Skip checking if the daily activity is set over")
    parser.add_option("-v", "--verbose", action = "store_true", dest = "verbose", default = False,
                      help = "make lots of noise for debugging")
    parser.add_option("-w", "--warnings", action = "store_true", dest = "warning", default = False,
                      help = "show useful warnings")
    parser.add_option("-z", "--rawzip", action = "store_true", dest = "compressed", default = False,
                      help = "compress output into raw.gz files")
    parser.add_option("--stderr", action = "store", type = "string", dest = "stderr",
                      help = "file for standard error")
    parser.add_option("--stdout", action = "store", type = "string", dest = "stdout",
                      help = "file for standard output")

    # Parse the command line
    (opts, args) = parser.parse_args()

    # Set global variables
    options.configfile = opts.configfile
    options.stderr = opts.stderr
    options.stdout = opts.stdout    
    options.date = opts.date 
    options.nocheck = opts.nocheck
    options.verbose = opts.verbose
    options.warning = opts.warning
    options.compressed = opts.compressed

    # The standardhandle has to be declared here, since verbose and warnings are options from the cli
    standardhandle.verbose(tag, "the options are {0}".format(opts))
    standardhandle.verbose(tag, "the argument is {0}".format(args))

    # Mapping the telescope argument to an option parameter (it might become an option in the future)
    if len(args) != 1:
        standardhandle.error(tag, "incorrect number of arguments, type -h for help", 2)
    elif args[0] == 'ST':
        standardhandle.error(tag, "not yet ready for telescope {0}".format(options.options.tel_id), 2)
    elif args[0] != 'LST1' and args[0] != 'M2':
        standardhandle.error(tag, "wrong telescope id, use 'LST1', 'LST2' or 'ST'", 2)
    options.tel_id = args[0]

    options.configfile = set_default_configfile_if_needed(command)
    options.date = set_default_date_if_needed()
    return args
##############################################################################
#
# set_default_date_if_needed
#
##############################################################################
def set_default_date_if_needed():
    tag = standardhandle.gettag()
    from .utils import is_defined
    if is_defined(options.date):
        return options.date
    else:
        from utils import getcurrentdate2
        from config import cfg
        return getcurrentdate2(cfg.get('MAGIC', 'DATESEPARATOR'))
##############################################################################
#
# set_default_directory_if_needed
#
##############################################################################
def set_default_directory_if_needed():
    tag = standardhandle.gettag()
    from osa.utils.utils import is_defined, getnightdirectory
    if is_defined(options.directory):
        return options.directory
    else:
        return getnightdirectory()
##############################################################################
#
# set_default_configfile_if_needed
#
##############################################################################
def set_default_configfile_if_needed(command):
    tag = standardhandle.gettag()

    """ The default config will be the name of the program, with suffix .cfg
        and present in the cfg subdir, trivial, isn't it? """ 

    from os.path import abspath, dirname, basename, join
    standardhandle.verbose(tag, "Command is {0}".format(command))
    if not options.configfile:
        command_dirname = dirname(abspath(command))
        command_basename = basename(command)
        config_basename = command_basename.replace('.py', '.cfg')
        options.configfile = join(command_dirname, 'cfg', config_basename)

    standardhandle.verbose(tag, "Setting default config file to {0}".format(options.configfile))
    return options.configfile
