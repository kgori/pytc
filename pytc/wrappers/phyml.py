#!/usr/bin/env python

from external import TreeSoftware
from ..errors.errors import filecheck
from ..readers.tree import Tree
from ..utils import fileIO
from ..utils.printing import print_and_return
import re

class Phyml(TreeSoftware):

    """ __init__ takes a Seq sequence record as 
    first positional argument, tmpdir as second, and supplied_binary= 
    as keyword argument """

    default_binary = 'phyml'
    score_regex = re.compile('(?<=Log-likelihood: ).+')
    local_dir = fileIO.path_to(__file__)

    def read(self, filename):
        tree_filename = filename + '_phyml_tree.txt'
        stats_filename = filename + '_phyml_stats.txt'
        self.add_tempfile(tree_filename)
        self.add_tempfile(stats_filename)
        with open(tree_filename) as treefile:
            with open(stats_filename) as statsfile:
                return (treefile.read(), statsfile.read())

    def run(self, analysis='nj', verbosity=0, **kwargs):
        if analysis is not None:
            self.set_default_flags(analysis)
        else:
            analysis = fileIO.basename(self.binary)
        if verbosity > 1:
            print self.flags
            print 'Writing tempfiles to', self.tmpdir
        filename = self.write()
        filecheck(filename)
        self.add_flag('-i', filename)
        if verbosity == 1:
            print_and_return('Running phyml on {0}'.format(self.record.name))
        elif verbosity > 1:
            print 'Running phyml on {0}'.format(self.record.name)
        (stdout, stderr) = self.call(verbose=(True if verbosity > 1 else False))
        (tree, stats) = self.read(filename)
        try:
            score = float(self.score_regex.search(stats).group(0))
        except:
            print tree
            print stats
        if verbosity > 1:
            print 'Cleaning tempfiles'
        self.clean()
        tree_object = Tree(newick=tree, score=score, program=analysis, 
            name=self.record.name, output=stats, **kwargs)
        self.record.tree = tree_object
        if verbosity > 1:
            print 'Done.'
        return tree_object

    def write(self):
        filename = self.record.get_name(default='tmp_phyml_input')
        filename = '{0}/{1}.phy'.format(self.tmpdir, filename)
        self.record.write_phylip(filename)
        self.add_tempfile(filename)
        return filename

    def read_datatype(self, datatype=None):
        datatype = datatype or self.record.datatype
        if datatype == 'protein':
            return {'-d': 'aa', '-m': 'WAG'}
        elif datatype == 'dna':
            return {'-d': 'nt', '-m': 'GTR'}

    def set_default_flags(self, analysis='nj', datatype=None):

        defaults = self.read_datatype(datatype=datatype)
        if defaults:
            defaults['-a'] = 'e'
            defaults['-b'] = 0
            defaults['-c'] = 4
            defaults['-q'] = ''
            defaults['--quiet'] = ''
            if analysis == 'ml' or analysis == 'full':
                defaults['-o'] = 'tlr'
            elif analysis == 'nj' or analysis == 'bionj':
                defaults['-o'] = 'n'
            elif analysis == 'lr' or analysis == 'bionj+':
                defaults['-o'] = 'lr'

            for flag in defaults:
                self.add_flag(flag, defaults[flag])

def runPhyml(rec, tmpdir, analysis, verbosity=0, **kwargs):
    p = Phyml(rec, tmpdir)
    return p.run(analysis, verbosity, **kwargs)
