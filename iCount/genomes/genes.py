"""
Extract largest possible gene segments from GTF file.
"""
import os
import logging

import pybedtools

import iCount
from iCount.genomes.segment import _filter_col8

LOGGER = logging.getLogger(__name__)


def get_genes(gtf_in, gtf_out, fai_file=None, name='gene', attribute='gene_id'):
    """
    Extract largest possible gene segments from input gtf file.

    Each gene can have multiple entries: for exons, introns, UTR...
    We wish to get a "maximal frame" of it's coordinates for given gene
    name, chromosome and strand.

    Parameters
    ----------
    gtf_in : str
        Absolute path to gtf input file.
    gtf_out : str
        Absolute path to BED6 output file.
    name : str
        Name for the 3rd column of output intervals.
    attribute : str
        Attribute to use as unique identifier for output intervals.

    Returns
    -------
    pybedtools.BedTool
        Sorted largest possible gene segments.

    """
    iCount.logger.log_inputs(LOGGER)
    # TODO: logstatements

    LOGGER.info('Reading fai file...')
    if fai_file:
        with open(fai_file) as fai:
            chromosomes = [line.strip().split()[0] for line in fai]

    data = {}

    LOGGER.info('Reading GTF input file...')
    for interval in pybedtools.BedTool(gtf_in):
        if fai_file and interval.chrom not in chromosomes:
            continue
        else:
            uniq = interval.attrs[attribute]  # unique identifier for `name`
            if uniq in data:
                if interval.start < data[uniq][1]:
                    data[uniq][1] = interval.start

                if interval.stop > data[uniq][2]:
                    data[uniq][2] = interval.stop

            else:
                data[uniq] = [interval.chrom, interval.start, interval.stop,
                              interval.strand, _filter_col8(interval)]

    LOGGER.info('Writing data to output GTF file...')
    gs = pybedtools.BedTool(pybedtools.create_interval_from_list(
        [chrom, '.', name, start, stop, '.', strand, '.', col8])
        for chrom, start, stop, strand, col8 in data.values()).saveas()

    gs1 = gs.sort().saveas(gtf_out)
    LOGGER.info('Results saved to {}.'.format(os.path.abspath(gs1.fn)))
    return os.path.abspath(gs1.fn)
