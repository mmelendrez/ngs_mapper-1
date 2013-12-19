from nose.tools import eq_, raises
from nose.plugins.attrib import attr
from mock import MagicMock, patch, Mock

from common import BaseClass
import fixtures

import os
from os.path import *

class Base(BaseClass):
    def create_file(self,filepath,contents):
        linecount = 0
        with open(filepath,'w') as fh:
            for line in contents.splitlines(True):
                fh.write(line)
                linecount += 1
        return linecount

@attr('current')
@patch('bwa.BWAMem',spec=True,run=Mock(return_value=0))
@patch('bwa.index_ref',spec=True,return_value=True)
class TestFunctionalRunBWA(Base):
    def test_bwa_mem_nonpaired(self,index_ref,bwamem):
        from run_bwa import bwa_mem
        result = bwa_mem( 'F.fq', mate=None, ref='ref.fna' )
        eq_( 'bwa.bam', result )

    def test_bwa_mem_paired(self,index_ref,bwamem):
        from run_bwa import bwa_mem
        result = bwa_mem( 'F.fq', mate='R.fq', ref='ref.fna' )
        eq_( 'bwa.bam', result )

    def test_bwa_mem_output_arg(self,index_ref,bwamem):
        from run_bwa import bwa_mem
        result = bwa_mem( 'F.fq', mate='R.fq', ref='ref.fna', output='file.bam' )
        eq_( 'file.bam', result )

    def test_bwa_mem_fails(self,index_ref,bwamem):
        from run_bwa import bwa_mem
        result = bwa_mem( 'F.fq', mate='R.fq', ref='ref.fna', output='file.bam' )
        eq_( -1, result )

    def test_ref_index_fails(self,index_ref,bwamem):
        from run_bwa import bwa_mem
        result = bwa_mem( 'F.fq', mate='R.fq', ref='ref.fna', output='file.bam' )
        eq_( -1, result )

class TestIntegrateRunBWA(Base):
    def setUp(self):
        self.read1,self.read2,self.ref = fixtures.get_sample_paired_reads()

    def test_maps_reads_paired(self):
        from run_bwa import bwa_mem
        eq_( 'bwa.bam', bwa_mem( self.read1, self.read2, ref=self.ref ) )
        assert exists( 'bwa.bam' ), "Did not create a bam file"
        assert os.stat('bwa.bam').st_size != 0, "Bam file created is zero bytes"

    def test_maps_reads_single(self):
        from run_bwa import bwa_mem
        eq_( 'bwa.bam', bwa_mem( self.read1, ref=self.ref ) )
        assert exists( 'bwa.bam' ), "Did not create a bam file"
        assert os.stat('bwa.bam').st_size != 0, "Bam file created is zero bytes"

    def test_output_param(self):
        from run_bwa import bwa_mem
        eq_( 'bwa.bam', bwa_mem( self.read1, ref=self.ref, output='file.bam' ) )
        assert exists( 'file.bam' ), "Did not create a bam file"
        assert os.stat('file.bam').st_size != 0, "Bam file created is zero bytes"

@patch('bwa.seqio.concat_files')
class TestFunctionalCompileReads(Base):
    def test_compile_reads_paired_and_unpaired(self,mock):
        from run_bwa import compile_reads
        outputdir = 'output'
        outputdir = join(self.tempdir,outputdir)
        # Should return/create 3 files
        reads = [('p1_1.fastq','p1_2.fastq'),'np1.fastq',('p2_1.fastq.fastq','p2_1.fastq.fastq'),'np2.fastq']
        files = ['F.fq','R.fq','NP.fq']
        expected = {
            'F':join(outputdir,files[0]),
            'R':join(outputdir,files[1]),
            'NP':join(outputdir,files[2])
        }
        eq_( expected, compile_reads( reads, outputdir ) )
        eq_( len(mock.call_args_list), 3 )

    def test_compile_reads_paired_only_single(self,mock):
        from run_bwa import compile_reads
        outputdir = 'output'
        outputdir = join(self.tempdir,outputdir)
        # Should return/create 3 files
        reads = [('p1_1.fastq','p1_2.fastq')]
        files = ['F.fq','R.fq','NP.fq']
        expected = {
            'F':join(outputdir,files[0]),
            'R':join(outputdir,files[1]),
            'NP':None
        }
        eq_( expected, compile_reads( reads, outputdir ) )
        eq_( len(mock.call_args_list), 2 )

    def test_compile_reads_paired_only_multiple(self,mock):
        from run_bwa import compile_reads
        outputdir = 'output'
        outputdir = join(self.tempdir,outputdir)
        # Should return/create 3 files
        reads = [('p1_1.fastq','p1_2.fastq'),('p2_1.fastq','p2_2.fastq')]
        files = ['F.fq','R.fq','NP.fq']
        expected = {
            'F':join(outputdir,files[0]),
            'R':join(outputdir,files[1]),
            'NP':None
        }
        eq_( expected, compile_reads( reads, outputdir ) )
        print mock.call_args_list
        eq_( len(mock.call_args_list), 2 )

    def test_compile_reads_unpaired_only_single(self,mock):
        from run_bwa import compile_reads
        outputdir = 'output'
        outputdir = join(self.tempdir,outputdir)
        # Should return/create 3 files
        reads = ['p1.fastq']
        files = ['F.fq','R.fq','NP.fq']
        expected = {
            'F':None,
            'R':None,
            'NP':join(outputdir,files[2])
        }
        eq_( expected, compile_reads( reads, outputdir ) )
        eq_( len(mock.call_args_list), 1 )

    def test_compile_reads_unpaired_only_multiple(self,mock):
        from run_bwa import compile_reads
        outputdir = 'output'
        outputdir = join(self.tempdir,outputdir)
        reads = ['p1.fastq','p2.fastq']
        files = ['F.fq','R.fq','NP.fq']
        expected = {
            'F':None,
            'R':None,
            'NP':join(outputdir,files[2])
        }
        eq_( expected, compile_reads( reads, outputdir ) )
        eq_( len(mock.call_args_list), 1 )

    def test_compile_reads_non_fastq(self,mock):
        from run_bwa import compile_reads, InvalidReadFile
        outputdir = join(self.tempdir,'output')
        reads = ['np.sff','np.ab1','np.fastq.gz']
        try:
            compile_reads( reads, outputdir )
            assert False, "Did not raise InvalidReadFile"
        except InvalidReadFile as e:
            pass
        except Exception as e:
            assert False, "Did not raise InvalidReadFile"

    def test_compile_reads_three_item_tuple(self,mock):
        from run_bwa import compile_reads, InvalidReadFile
        outputdir = join(self.tempdir,'output')
        reads = [('one.fastq','two.fastq','three.fastq')]
        try:
            compile_reads( reads, outputdir )
            assert False, "ValueError not raised"
        except ValueError as e:
            pass

    def test_compile_reads_emptyreadfilelist(self,mock):
        from run_bwa import compile_reads, InvalidReadFile
        outputdir = join(self.tempdir,'output')
        reads = ['np.sff','np.ab1','np.fastq.gz']
        eq_({'F':None,'R':None,'NP':None}, compile_reads( [], outputdir ) )

class TestIntegrationCompileReads(Base):
    def test_compile_reads_outputdir_not_exist(self):
        outputdir = join(self.tempdir,'output')
        self.run_compile_reads(outputdir)

    def test_compile_reads_outputdir_exists(self):
        outputdir = join(self.tempdir,'output')
        os.mkdir(outputdir)
        self.run_compile_reads(outputdir)

    def run_compile_reads(self,outputdir):
        from run_bwa import compile_reads
        reads = [('p1_1.fastq','p1_2.fastq'),'np1.fastq',('p2_1.fastq','p2_2.fastq'),'np2.fastq']
        read_contents = '@Read1\nATGCATGCATGC\n+\n111111111111\n'
        # Create all the files
        expected_linecounts = {'F':0,'R':0,'NP':0}
        for read in reads:
            if len(read) == 2:
                f = self.create_file(read[0],read_contents)
                r = self.create_file(read[1],read_contents)
                expected_linecounts['F'] += f
                expected_linecounts['R'] += r
            else:
                np = self.create_file(read,read_contents)
                expected_linecounts['NP'] += np

        result = compile_reads( reads, outputdir )
        assert os.access(result['F'],os.R_OK), "Did not create Forward file"
        assert os.access(result['R'],os.R_OK), "Did not create Reverse file"
        assert os.access(result['NP'],os.R_OK), "Did not create NonPaired file"
        for k,v in expected_linecounts.items():
            with open(result[k]) as fh:
                contents = fh.read()
                print contents
                eq_( v, len(contents.splitlines()) )
