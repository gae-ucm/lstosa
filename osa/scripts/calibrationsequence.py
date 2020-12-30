"""
Script to process the calibration runs and produce the
DRS4 pedestal, charge and time calibration files.
"""
import logging
import os
import subprocess
import sys
from os import path
from pathlib import Path

import lstchain.visualization.plot_calib as calib
import lstchain.visualization.plot_drs4 as drs4
import matplotlib.pyplot as plt

from osa.configs import options
from osa.configs.config import cfg
from osa.jobs.job import historylevel
from osa.reports.report import history
from osa.utils.cliopts import calibrationsequencecliparsing
from osa.utils.logging import MyFormatter
from osa.utils.standardhandle import stringify

log = logging.getLogger(__name__)


def calibrationsequence(args):
    """
    Handle the three steps for creating the calibration products:
    DRS4 pedestal, charge calibration and time calibration files

    Parameters
    ----------
    args

    Returns
    -------
    Return code

    """
    # FIXME: add input arguments explicitly
    pedestal_filename = args[0]
    calibration_filename = args[1]
    ped_run_number = args[2]
    cal_run_number = args[3]

    history_file = path.join(
        options.directory, f"sequence_{options.tel_id}_{cal_run_number}.history"
    )
    level, rc = historylevel(history_file, "CALIBRATION")
    log.info(f"Going to level {level}")
    if level == 3:
        rc = drs4_pedestal(ped_run_number, pedestal_filename, history_file)
        level -= 1
        log.info(f"Going to level {level}")
    if level == 2:
        rc = calibrate_charge(
            ped_run_number,
            cal_run_number,
            pedestal_filename,
            calibration_filename,
            history_file,
        )
        level -= 1
        log.info(f"Going to level {level}")
    if level == 1:
        rc = calibrate_time(cal_run_number, pedestal_filename, calibration_filename, history_file)
        level -= 1
        log.info(f"Going to level {level}")
    if level == 0:
        log.info(f"Job for sequence {ped_run_number} finished without fatal errors")
    return rc


def drs4_pedestal(run_ped, pedestal_output_file, history_file):
    """
    Create a DRS4 pedestal file

    Parameters
    ----------
    run_ped
    pedestal_output_file
    history_file

    Returns
    -------
    Return code

    """
    rawdata_path = Path(cfg.get("LST1", "RAWDIR"))
    # Get raw data run regardless when was taken
    run_drs4_file_list = [
        file for file in rawdata_path.rglob(f'*/{cfg.get("LSTOSA", "R0PREFIX")}.Run{run_ped}.0000*')
    ]
    if run_drs4_file_list:
        input_file = str(run_drs4_file_list[0])
    else:
        log.error(f"Files corresponding to DRS4 pedestal run {run_ped} not found")
        sys.exit(1)

    calib_configfile = None
    output_file = path.join(options.directory, pedestal_output_file)
    command_args = [
        cfg.get("PROGRAM", "PEDESTAL"),
        "--input-file=" + input_file,
        "--output-file=" + output_file,
    ]
    command_concept = "drs4_pedestal"

    try:
        log.info(f"Executing {stringify(command_args)}")
        rc = subprocess.call(command_args)
    except OSError as error:
        history(
            run_ped,
            options.calib_prod_id,
            command_concept,
            pedestal_output_file,
            calib_configfile,
            error,
            history_file,
        )
        log.exception(f"Could not execute {stringify(command_args)}, error: {error}")
    except subprocess.CalledProcessError as error:
        log.exception(f"{error}, {rc}")
    else:
        history(
            run_ped,
            options.calib_prod_id,
            command_concept,
            pedestal_output_file,
            calib_configfile,
            rc,
            history_file,
        )

    if rc != 0:
        sys.exit(rc)

    plot_file = path.join(options.directory, "log", f"drs4_pedestal.Run{run_ped}.0000.pdf")
    log.info(f"Producing plots in {plot_file}")
    drs4.plot_pedestals(
        input_file,
        output_file,
        run_ped,
        plot_file,
        tel_id=1,
        offset_value=300,
    )
    plt.close("all")

    return rc


def calibrate_charge(
    run_ped, calibration_run, pedestal_file, calibration_output_file, history_file
):
    """
    Create a charge calibration file to transform from ADC counts to photo-electrons

    Parameters
    ----------
    run_ped
    calibration_run
    pedestal_file
    calibration_output_file
    history_file

    Returns
    -------
    Return code

    """

    rawdata_path = Path(cfg.get("LST1", "RAWDIR"))
    # Get raw data run regardless when was taken
    run_calib_file_list = [
        file
        for file in rawdata_path.rglob(
            f'*/{cfg.get("LSTOSA", "R0PREFIX")}.Run{calibration_run}.0000*'
        )
    ]
    if run_calib_file_list:
        calibration_run_file = str(run_calib_file_list[0])
    else:
        log.error(f"Files corresponding to calibration run {calibration_run} not found")
        sys.exit(1)

    calib_configfile = cfg.get("LSTOSA", "CALIBCONFIGFILE")
    output_file = path.join(options.directory, calibration_output_file)
    log_output_file = path.join(
        options.directory, "log", f"calibration.Run{calibration_run}.0000.log"
    )
    command_args = [
        cfg.get("PROGRAM", "CALIBRATION"),
        "--input_file=" + calibration_run_file,
        "--output_file=" + output_file,
        "--pedestal_file=" + pedestal_file,
        "--config=" + calib_configfile,
        "--log_file=" + log_output_file,
    ]
    command_concept = "charge_calibration"

    try:
        log.info(f"Executing {stringify(command_args)}")
        rc = subprocess.call(command_args)
    except OSError as error:
        history(
            calibration_run,
            options.calib_prod_id,
            command_concept,
            calibration_output_file,
            path.basename(calib_configfile),
            error,
            history_file,
        )
        log.exception(f"Could not execute {stringify(command_args)}, error: {error}")
    except subprocess.CalledProcessError as error:
        log.exception(f"{error}, {rc}")
    else:
        history(
            calibration_run,
            options.calib_prod_id,
            command_concept,
            calibration_output_file,
            path.basename(calib_configfile),
            rc,
            history_file,
        )

    if rc != 0:
        sys.exit(rc)

    plot_file = path.join(
        options.directory,
        "log",
        f"calibration.Run{calibration_run}.0000.pedestal.Run{run_ped}.0000.pdf",
    )
    calib.read_file(output_file, tel_id=1)
    log.info(f"Producing plots in {plot_file}")
    calib.plot_all(calib.ped_data, calib.ff_data, calib.calib_data, calibration_run, plot_file)
    plt.close("all")

    return rc


def calibrate_time(calibration_run, pedestal_file, calibration_output_file, history_file):
    """
    Create a time calibration file

    Parameters
    ----------
    calibration_run
    pedestal_file
    calibration_output_file
    history_file

    Returns
    -------
    Return code

    """
    calibration_data_files = (
        f'{cfg.get("LST1", "RAWDIR")}/*/'
        f'{cfg.get("LSTOSA", "R0PREFIX")}.Run{calibration_run}.*{cfg.get("LSTOSA", "R0SUFFIX")}'
    )
    calib_configfile = cfg.get("LSTOSA", "CALIBCONFIGFILE")
    time_calibration_output_file = path.join(options.directory, f"time_{calibration_output_file}")
    command_args = [
        cfg.get("PROGRAM", "TIME_CALIBRATION"),
        "--input-file=" + calibration_data_files,
        "--output-file=" + time_calibration_output_file,
        "--pedestal-file=" + pedestal_file,
        "--config=" + calib_configfile,
    ]
    command_concept = "time_calibration"

    try:
        log.info(f"Executing {stringify(command_args)}")
        rc = subprocess.call(command_args)
    except OSError as error:
        history(
            calibration_run,
            options.calib_prod_id,
            command_concept,
            path.basename(time_calibration_output_file),
            path.basename(calib_configfile),
            error,
            history_file,
        )
        log.exception(f"Could not execute {stringify(command_args)}, error: {error}")
    except subprocess.CalledProcessError as error:
        log.exception(f"{error}, {rc}")
    else:
        history(
            calibration_run,
            options.calib_prod_id,
            command_concept,
            path.basename(time_calibration_output_file),
            path.basename(calib_configfile),
            rc,
            history_file,
        )

    if rc == 1:
        log.warning(
            "Not able to create time calibration file. Creating a link "
            "to default calibration time file corresponding to run 1625"
        )
        def_time_calib_run = cfg.get("LSTOSA", "DEFAULT-TIME-CALIB-RUN")
        calibpath = Path(cfg.get("LST1", "CALIBDIR"))
        outputf = time_calibration_output_file
        file_list = [
            file
            for file in calibpath.rglob(
                f"*/{options.calib_prod_id}/time_calibration.Run{def_time_calib_run}*"
            )
        ]
        if file_list:
            log.info(
                "Creating a symlink to the default calibration"
                "time file corresponding to run 1625"
            )
            inputf = file_list[0]
            os.symlink(inputf, outputf)
            rc = 0
            history(
                calibration_run,
                options.calib_prod_id,
                command_concept,
                path.basename(time_calibration_output_file),
                path.basename(calib_configfile),
                rc,
                history_file,
            )
        else:
            log.error("Default time calibration file not found. Create it first.")
            sys.exit(1)

    return rc


if __name__ == "__main__":
    # Set the options through cli parsing
    args = calibrationsequencecliparsing(sys.argv[0])

    # Logging
    fmt = MyFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(fmt)
    logging.root.addHandler(handler)
    if options.verbose:
        logging.root.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    # run the routine
    rc = calibrationsequence(args)
    sys.exit(rc)
