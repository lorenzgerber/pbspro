
"""

/* 
#  Copyright (C) 1994-2017 Altair Engineering, Inc.
#  For more information, contact Altair at www.altair.com.
#   
#  This file is part of the PBS Professional ("PBS Pro") software.
#  
#  Open Source License Information:
#   
#  PBS Pro is free software. You can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free 
#  Software Foundation, either version 3 of the License, or (at your option) any 
#  later version.
#   
#  PBS Pro is distributed in the hope that it will be useful, but WITHOUT ANY 
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#   
#  You should have received a copy of the GNU Affero General Public License along 
#  with this program.  If not, see <http://www.gnu.org/licenses/>.
#   
#  Commercial License Information: 
#  
#  The PBS Pro software is licensed under the terms of the GNU Affero General 
#  Public License agreement ("AGPL"), except where a separate commercial license 
#  agreement for PBS Pro version 14 or later has been executed in writing with Altair.
#   
#  Altair’s dual-license business model allows companies, individuals, and 
#  organizations to create proprietary derivative works of PBS Pro and distribute 
#  them - whether embedded or bundled with other software - under a commercial 
#  license agreement.
#  
#  Use of Altair’s trademarks, including but not limited to "PBS™", 
#  "PBS Professional®", and "PBS Pro™" and Altair’s logos is subject to Altair's 
#  trademark licensing policies.
 *
 */
"""
__doc__ = """
This module is used for SGI systems.
"""

import pbs
import os
import sys
from pbs.v1._pmi_types import BackendError
from pbs.v1._pmi_utils import _pbs_conf, _get_hosts

pbsexec = _pbs_conf("PBS_EXEC")
if pbsexec is None:
    raise BackendError("PBS_EXEC not found")

sys.path.append(os.path.join(pbsexec, "python", "lib", "python2.7"))
sys.path.append(os.path.join(pbsexec, "python", "lib", "python2.7",
                "lib-dynload"))
import encodings


# Plug in the path for the SGI power API.
sys.path.append("/opt/sgi/ta")
import sgi_power_api as api


class Pmi:
    def __init__(self, pyhome=None):
        pbs.logmsg(pbs.LOG_DEBUG, "SGI: init")
        api.SERVER = """lead-eth:8888"""

    def _connect(self, endpoint, port):
        pbs.logmsg(pbs.LOG_DEBUG, "SGI: connect")
        api.VerifyConnection()
        return

    def _disconnect(self):
        pbs.logmsg(pbs.LOG_DEBUG, "SGI: disconnect")
        return

    def _get_usage(self, job):
        pbs.logjobmsg(job.id, "SGI: get_usage")
        report = api.MonitorReport(job.id)
        if report is not None and report[0] == 'total_energy':
            pbs.logjobmsg(job.id, "SGI: energy %fkWh" % report[1])
            return report[1]
        return None

    def _query(self, query_type):
        pbs.logmsg(pbs.LOG_DEBUG, "SGI: query")
        if query_type == pbs.Power.QUERY_PROFILE:
            return api.ListAvailableProfiles()
        return None

    def _activate_profile(self, profile_name, job):
        pbs.logmsg(pbs.LOG_DEBUG, "SGI: %s activate '%s'" %
                   (job.id, str(profile_name)))
        api.NodesetCreate(job.id, _get_hosts(job))
        api.MonitorStart(job.id, profile_name)
        return False

    def _deactivate_profile(self, job):
        pbs.logmsg(pbs.LOG_DEBUG, "SGI: deactivate")
        try:
            api.MonitorStop(job.id)
        finally:	# be sure to remove the nodeset
            api.NodesetDelete(job.id)
        return False
