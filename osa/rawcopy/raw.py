from osa.utils.standardhandle import verbose, warning, error, output, gettag
from osa.utils import options, cliopts
from osa.configs import config

def arerawfilestransferredfortel(tel_id):
    tag = gettag()
    from os.path import join, exists
    from osa.utils.utils import lstdate_to_dir
    nightdir = lstdate_to_dir(options.date)
    dir = join(config.cfg.get(tel_id, 'ENDOFRAWTRANSFERDIR'), nightdir)
    flagfile = join(dir, config.cfg.get('LSTOSA', 'ENDOFACTIVITYPREFIX'))

    if exists(flagfile):
        output(tag, "Files for {0} {1} are completely transferred to raid".format(options.date, tel_id))
        return True
    else:
        warning(tag, "File {0} not found!".format(flagfile))
        output(tag, "Files for {0} {1} are not yet transferred to raid. Expecting more raw data".format(options.date, tel_id))
        return False


def arerawfilestransferred():
    tag = gettag()
    answer = None
    if options.tel_id == 'ST':
        answer_LST1 = arerawfilestransferredfortel('LST1')
        answer_LST2 = arerawfilestransferredfortel('LST2')
        answer = answer_LST1 * answer_LST2
    else:
        answer = arerawfilestransferredfortel(options.tel_id)
    return answer


def get_check_rawdir():
    tag = gettag()
    from os.path import exists, join
    rawdir = getrawdir()
    rawsuffix = config.cfg.get('LSTOSA', 'RAWSUFFIX')
    verbose(tag, f"raw suffix = {rawsuffix}")
    compressedsuffix = config.cfg.get('LSTOSA', 'COMPRESSEDSUFFIX')
    verbose(tag, f"raw compressed suffix = {rawsuffix + compressedsuffix}")
    print(rawdir)

    if not exists(rawdir):
        # The most sensible thing to do is to quit succesfully after a warning
        # warning (tag, 'rawdir set to . because ' + rawdir + ' does not exists!')
        # rawdir = os.getcwd()
        error(tag, "Raw directory {0} does not exist".format(rawdir), 2)
    else:
        # Check that it contains at least one raw or compressed-raw file and set compression flag
        from glob import glob
        list = glob(join(rawdir, '*' + rawsuffix))
        listz = glob(join(rawdir, '*' + rawsuffix + compressedsuffix))
        if (len(list) + len(listz)) == 0:
            error(tag, "Empty raw directory {0}".format(rawdir), 5)
        elif len(list) !=0 and len(listz) !=0:
            warning(tag, "Both, compressed and not compressed filex co-existing in {0}".format(rawdir))
        elif len(listz) != 0:
            options.compressed = True
            verbose(tag, "Compressed option flag set")
    verbose(tag, "Raw directory: {0}".format(rawdir))
    return rawdir

def getrawdir():
    tag = gettag()
    from os.path import join
    from osa.configs import config
    rawdir = None
    if options.tel_id == 'LST1' or options.tel_id == 'LST2':
        rawdir = join(config.cfg.get(options.tel_id, 'RAWDIR'), options.date)
    return rawdir

def getreportdir():
    tag = gettag()
    from os.path import exists, join
    reportdir = join(config.cfg.get(options.tel_id, 'REPORTDIR'), options.date)
    reportsuffix = config.cfg.get('LSTOSA', 'REPORTSUFFIX')
    if not exists(reportdir):
        # The most sensible thing to do is to quit succesfully after a warning
        # warning (tag, 'rawdir set to . because ' + rawdir + ' does not exists!')
        # rawdir = os.getcwd()
        error(tag, "Report directory {0} does not exist".format(reportdir), 2)
    else:
        # Check that it contains at least one raw or compressed-raw file and set compression flag
        from glob import glob
        list = glob(join(reportdir, '*' + reportsuffix))
      
        if len(list) == 0:
            error(tag, "Empty report directory {0}".format(reportdir), 5)
    verbose(tag, "Report directory: {0}".format(reportdir))
    return reportdir
