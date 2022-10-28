import numpy as np
import gzip as gz
from .._math import str2bool
from ..small_tools import str_decode

def read_outcar( outcar ):
    if '.gz' in outcar:
        with gz.open( outcar, 'rb' ) as f:
            lines = f.readlines( )
        decode = True
    else:
        with open( outcar, 'r' ) as f:
            lines = f.readlines( )
        decode = False

    return lines, decode

def if_vasp_done( outcar ):
    job_done = False
    lines, decode = read_outcar( outcar )
    if 'Voluntary context switches' in str_decode( lines[ -1 ], decode) :
        job_done = True
    return job_done


def get_lines_outcar( outcar ):
    #if '.gz' in outcar:
    #    with gz.open( outcar, 'rb' ) as f:
    #        lines = f.readlines( )
    #    decode = True
    #else:
    #    with open( outcar, 'r' ) as f:
    #        lines = f.readlines( )
    #    decode = False  
    lines, decode = read_outcar( outcar )
    #Check if calculation is done

    job_done = False
    for iline in range( len( lines ) - 1, -1, -1 ):
        if 'General timing and accounting informations for this job' in str_decode( lines[ iline ], decode ):
            job_done = True
            break
    if not job_done:
        print ( "WARNING: perhaps OUTCAR is for an imcompleted calculation" )
        print ( "Please check: ", outcar )

    return lines, decode

def get_calculation_details( outcar ):
    
    lines, decode = get_lines_outcar( outcar )
    
    NSW = 0
    EFIELD = 0
    for iline in range( len( lines ) - 1, -1, -1 ):
  
        if "PREC " in str_decode( lines[ iline ], decode ):
            PREC = lines[ iline ].split( )[ 2 ] 

        if "ENCUT " in str_decode( lines[ iline ], decode ):
            ENCUT = float( lines[ iline ].split( )[ 2 ] )
      
        if "LREAL " in str_decode( lines[ iline ] ):
            LREAL = str2bool( lines[ iline ].split( )[ 2 ] )

        if "EDIFF " in str_decode( lines[ iline ], decode ) and '=' in str_decode( lines[ iline ], decode ):
            EDIFF = float( lines[ iline ].split( )[ 2 ] )

        if "EDIFFG" in str_decode( lines[ iline ], decode ):
            EDIFFG = float( lines[ iline ].split( )[ 2 ] )

        if "ISMEAR" in str_decode( lines[ iline ], decode ):
            ISMEAR = int( lines[ iline ].split( )[ 2 ].replace( ';', '' ) ) 
            SIGMA  = float( lines[ iline ].split( )[ 5 ] )

        if "NBANDS" in lines[ iline ]:
            NKPTS = int( lines[ iline ].split( )[ 3 ].replace( ';', '' ) )
            NBANDS = int( lines[ iline ].split( )[ 14 ] )

        if "NELECT" in lines[ iline ]:
            NELECT = float( lines[ iline ].split( )[ 2 ].replace( ';', '' ) )

        if "NSW" in lines[ iline ] and "=" in lines[ iline ]:
            NSW = float( lines[ iline ].split( )[ 2 ].replace( ';', '' ) )
   
        if "EFIELD" in lines[ iline ] and '=' in lines[ iline ]:
            EFIELD = float( lines[ iline ].split( )[ 2 ] )

    k = np.zeros( [ NKPTS, 4] )  # coordinates + weight
    for iline in range( len( lines ) - 1, -1, -1 ):
        if 'Following reciprocal coordinates:' in lines[ iline ]:
            break
    for ik in range( NKPTS ):
        k[ ik ] = np.array( lines[ iline + 2 + ik ].split( ), dtype = float )

    details = { 
                "PREC"       : PREC,
                "LREAL"      : LREAL,
                "ENCUT"      : ENCUT,
                "EDIFF"      : EDIFF,
                "EDIFFG"     : EDIFFG,
                "ISMEAR"     : ISMEAR,
                "SIGMA"      : SIGMA,
                "NKPTS"      : NKPTS,
                "NBANDS"     : NBANDS,
                "NELECT"     : NELECT,
                "NSW"        : NSW,
                "EFIELD"     : EFIELD
              }

    del lines

    return details, k
    

def get_energy( outcar ):

    ener = 100000.
    lines, decode = get_lines_outcar( outcar )

    for iline in range( len( lines ) - 1, -1, -1 ):
        if "energy  w" in str_decode( lines[ iline ], decode ):
            ener = float( lines[ iline ].split( )[ 6 ] )
            break

    del lines

    return ener

def get_efermi( outcar ):

    lines, decode = get_lines_outcar( outcar )

    for iline in range( len( lines ) - 1, -1, -1 ):
        if "E-fermi" in str_decode( lines[ iline ], decode ):
            efermi = float( lines[ iline ].split( )[ 2 ] )
            break

    del lines

    return efermi


def get_corelevel( outcar ):
    lines, decode  = get_lines_outcar( outcar )
    data = {}
    for i in range( len( lines ) ):
        line = str_decode( lines[ i ], decode )
        if "the core state eigenenergies are" in line:
            startline = i + 1
            break

    for i in range( startline, len( lines ) ):
        line = str_decode( lines[ i ], decode )
        tmp = line.split()
        if line.strip() == "":
            break
        if tmp[ 0 ][ -1 ] == "-":
            at = int( tmp[ 0 ].replace( '-','') ) - 1 #To match index of ase
            data[ at ] = {}
            for j in range( len( tmp ) ):
                if tmp[ j ][-1] in [ 's', 'p', 'd', 'f' ]:
                    data[ at ][ tmp[ j ] ] = float( tmp[ j+1 ] )
        else:
            for j in range( len( tmp ) ):
                if tmp[ j ][-1] in [ 's', 'p', 'd', 'f' ]:
                    data[ at ][ tmp[ j ] ] = float( tmp[ j+1 ] )

    return data


