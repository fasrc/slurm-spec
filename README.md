# slurm.spec

This is our master slurm.spec file we use for building slurm in RC.

## Usage

For each version of slurm make a branch and then use that branch to build it.  Note that the slurm.spec that SchedMD provides does change periodically (especially for major releases).  Thus one should always compare our spec against theirs and use theirs as the template.  Our modifications should always sit on top of theirs.

For the record the master branch is for 16.05.3-1fasrc01
