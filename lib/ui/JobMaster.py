import commands
import os
import time
import sys
from taskbuffer.JobSpec import JobSpec
from taskbuffer.FileSpec import FileSpec
from common.KILogger import KILogger
from ui.Actions import moveData
import userinterface.Client as Client
_logger = KILogger().getLogger("JobMaster")

class JobMaster:
    def __init__(self):
        self.jobList = []
        self.fileList = []

    def putData(self, params=None, fileList=[], fromSEparams=None, toSEparams=None):
        return moveData(params=params, fileList=fileList, params1=fromSEparams, params2=toSEparams)

    def getTestJob(self, site):
        datasetName = 'panda.destDB.%s' % commands.getoutput('uuidgen')
        destName    = 'ANALY_RRC-KI-HPC'

        job = JobSpec()
        job.jobDefinitionID   = int(time.time()) % 10000
        job.jobName           = "%s" % commands.getoutput('uuidgen')
        job.transformation    = '/s/ls2/users/poyda/bio/runbio_wr.py'
        job.destinationDBlock = datasetName
        job.destinationSE     = destName
        job.currentPriority   = 1000
        job.prodSourceLabel   = 'user'
        job.computingSite     = site
        job.cloud             = 'RU'

        job.jobParameters=""

        fileOL = FileSpec()
        fileOL.lfn = "%s.job.log.tgz" % job.jobName
        fileOL.destinationDBlock = job.destinationDBlock
        fileOL.destinationSE     = job.destinationSE
        fileOL.dataset           = job.destinationDBlock
        fileOL.type = 'log'
        fileOL.scope = 'panda'
        job.addFile(fileOL)
        return job

    def submitJobs(self, jobList):
        print 'Submit jobs'
        _logger.debug('Submit jobs')

        s,o = Client.submitJobs(jobList)
        _logger.debug("---------------------")
        _logger.debug(s)
        for x in o:
            _logger.debug("PandaID=%s" % x[0])

    def sendjob(self, data):
        _logger.debug('SendJob with params: ' + ' '.join(params))

        datasetName = 'panda:panda.destDB.%s' % commands.getoutput('uuidgen')
        destName    = 'ANALY_RRC-KI-HPC'
        site = 'ANALY_RRC-KI-HPC'
        scope = 'user.ruslan'

        executable = data['executable']
        parameters = data['parameters']
        input_type = data['input_type']
        input_params = data['input_params']
        input_files = data['input_files']
        output_type = data['output_type']
        output_params = data['output_params']
        output_files = data['output_files']

        jparams = parameters

        if not executable.startswith('/s/ls/users/poyda'):
            _logger.error('Illegal distr name')
            return


        job = JobSpec()
        job.jobDefinitionID = int(time.time()) % 10000
        job.jobName = commands.getoutput('uuidgen')
        job.transformation = executable
        job.destinationDBlock = datasetName
        job.destinationSE = destName
        job.currentPriority = 1000
        job.prodSourceLabel = 'user'
        job.computingSite = site
        job.cloud = 'RU'
        job.prodDBlock = "%s:%s.%s" % (scope, scope, job.jobName)

        job.jobParameters = jparams

        fileIT = FileSpec()
        fileIT.lfn = '%s.%s.input.tgz' % (scope, job.jobName)
        fileIT.dataset = job.prodDBlock
        fileIT.prodDBlock = job.prodDBlock
        fileIT.type = 'input'
        fileIT.scope = scope
        job.addFile(fileIT)

        for file in output_files:
            fileOT = FileSpec()
            fileOT.lfn = file
            fileOT.destinationDBlock = job.prodDBlock
            fileOT.destinationSE = job.destinationSE
            fileOT.dataset = job.prodDBlock
            fileOT.type = 'output'
            fileOT.scope = scope
            fileOT.GUID = commands.getoutput('uuidgen')
            job.addFile(fileOT)


        fileOL = FileSpec()
        fileOL.lfn = "%s.log.tgz" % job.jobName
        fileOL.destinationDBlock = job.destinationDBlock
        fileOL.destinationSE = job.destinationSE
        fileOL.dataset = job.destinationDBlock
        fileOL.type = 'log'
        fileOL.scope = 'panda'
        job.addFile(fileOL)

        params = {'compress': True,
                  'tgzname': fileIT.lfn}
        _logger.debug('MoveData')
        ec = (0, '')
        ec = self.putData(params=params, fileList=input_files, fromType=input_type, fromParams=input_params, toType='grid', toParams={'dest': fileIT.dataset})
        if ec[0] != 0:
            _logger.error('Move data error: ' + ec[1])
            return
        self.jobList.append(job)
        self.run()


    def run(self):
        for job in self.jobList:
            jobs = []
            #jobs.append(self.getBuildJob(job))
            #jobs.append(self.getStageInJob(job))
            #jobs.append(self.getExecuteJob(job))
            #jobs.append(self.getStageOutJob(job))

        self.submitJobs(self.jobList)


