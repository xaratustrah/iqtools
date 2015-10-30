"""


================================================================
                Standalone Python TDMS reader, 
   (not using the NI libraries for they were Windows-specific)
================================================================


based on the format description on
http://zone.ni.com/devzone/cda/tut/p/id/5696



Floris van Vugt
IMMM Hannover
http://florisvanvugt.free.fr/


I am greatly indebted for insightful bug-corrections by:
ADAM REEVE
JUERGEN NEUBAUER, PH.D.

Thanks guys!


"""



# S. Klanke: 
#  * Fixed a few print-statements and integer divisons for Python 3 compatibility
#  * Use arrays for drastic speed improvements


import struct
import os
import array




# Tells us whether we should really output messages about what
# we have read (clutters the output buffer though)
verbose = False


# store previous values for the raw data properties for when
# they are repeated
object_rawdata = {}


def byteToHex( byteStr ):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """
    
    # Uses list comprehension which is a fractionally faster implementation than
    # the alternative, more readable, implementation below
    #   
    #    hex = []
    #    for aChar in byteStr:
    #        hex.append( "%02X " % ord( aChar ) )
    #
    #    return ''.join( hex ).strip()        

    return ''.join( [ "%02X " % ord( x ) for x in byteStr ] ).strip()








tocProperties = {
    'kTocMetaData'         : (1<<1),
    'kTocRawData'          : (1<<3),
    'kTocDAQmxRawData'     : (1<<7),
    'kTocInterleavedData'  : (1<<5),
    'kTocBigEndian'        : (1<<6),
    'kTocNewObjList'       : (1<<2),
    }







tdsDataTypes = [
    'tdsTypeVoid',
    'tdsTypeI8',    
    'tdsTypeI16',
    'tdsTypeI32',    
    'tdsTypeI64',
    'tdsTypeU8',    
    'tdsTypeU16',    
    'tdsTypeU32',    
    'tdsTypeU64',
    'tdsTypeSingleFloat',    
    'tdsTypeDoubleFloat',    
    'tdsTypeExtendedFloat',    
    'tdsTypeSingleFloatWithUnit',    
    'tdsTypeDoubleFloatWithUnit',    
    'tdsTypeExtendedFloatWithUnit',
    'tdsTypeString',   
    'tdsTypeBoolean',   
    'tdsTypeTimeStamp',   
    'tdsTypeDAQmxRawData',
]


tdsDataTypesDefined = {
    0x19: 'tdsTypeSingleFloatWithUnit',    
    0x20: 'tdsTypeString',   
    0x21: 'tdsTypeBoolean',   
    0x44: 'tdsTypeTimeStamp',   
    0xFFFFFFFF:'tdsTypeDAQmxRawData',
}



tdsDataTypesTranscriptions = {
    'tdsTypeVoid'                  : '',
    'tdsTypeI8'                    : 'b',
    'tdsTypeI16'                   : 'h', # short: standard size: 2 bytes
    'tdsTypeI32'                   : 'l',
    'tdsTypeI64'                   : 'q',
    'tdsTypeU8'                    : 'B',
    'tdsTypeU16'                   : 'H', # unsigned short: 2 bytes
    'tdsTypeU32'                   : 'L',
    'tdsTypeU64'                   : 'Q',
    'tdsTypeSingleFloat'           : 'f',
    'tdsTypeDoubleFloat'           : 'd',
    'tdsTypeExtendedFloat'         : ' ', #NOT YET IMPLEMENTED
    'tdsTypeSingleFloatWithUnit'   : ' ', #NOT YET IMPLEMENTED
    'tdsTypeDoubleFloatWithUnit'   : ' ', #NOT YET IMPLEMENTED
    'tdsTypeExtendedFloatWithUnit' : ' ', #NOT YET IMPLEMENTED
    'tdsTypeString'                :' ', # SHOULD BE HANDLED SEPARATELY
    'tdsTypeBoolean'               :'b',
    'tdsTypeTimeStamp'             :' ', # SHOULD BE HANDLED SEPARATELY
    'tdsTypeDAQmxRawData'          :' ', # SHOULD BE HANDLED SEPARATELY
}





def dataTypeFrom( s ):
    """
    Find back the data type from
    raw input data.
    """
    repr = struct.unpack("<L", s)[0]
    if (repr in tdsDataTypesDefined.keys()):
        return tdsDataTypesDefined[repr]
    else:
        return tdsDataTypes[repr]



def dataTypeLength( datatype ):
    """
    How many bytes we need to read to
    read in an object of the given datatype
    """

    if (datatype in ['tdsTypeVoid']):
        return 0

    if (datatype in ['tdsTypeI8','tdsTypeU8','tdsTypeBoolean']):
        return 1

    if (datatype in ['tdsTypeI16','tdsTypeU16']):
        return 2

    if (datatype in ['tdsTypeI32','tdsTypeU32','tdsTypeSingleFloat','tdsTypeSingleFloatWithUnit']):
        return 4

    if (datatype in ['tdsTypeI64','tdsTypeU64','tdsTypeDoubleFloat','tdsTypeDoubleFloatWithUnit']):
        return 8

    if (datatype in ['tdsTypeTimeStamp']):
        return 16


    if (datatype in [
            'tdsTypeString',
            'tdsTypeExtendedFloat',    
            'tdsTypeExtendedFloatWithUnit',
            'tdsTypeDAQmxRawData',
            ]):
        return False



    


def dataTypeTranscription( datatype ):
    """
    Returns the identifier for the given datatype
    that we need to feed into struct.unpack to get
    the right thing out.
    """
    return tdsDataTypesTranscriptions[datatype]


    





def getValue( s, endianness, datatype ):
    """
    We just read s from the file,
    and now we need to unpack it.
    """

    if datatype=='tdsTypeTimeStamp':
        t = struct.unpack(endianness+"Qq", s)

        return (t[1],         # the number of seconds since the 1904 epoch
                t[0]*(2**-64) # plus the number of 2^-64 seconds
                )
        
    else:
        code = endianness+dataTypeTranscription(datatype)
        return struct.unpack(code, s)[0]


    return False






def readLeadIn( f ):
    """
    Read the lead-in of a segment
    """


    
    s = f.read(4) # read 4 bytes
    if (not s in [b'TDSm']):
        print ("Error: segment does not start with TDSm, but with ",s)
        exit()

    
    s = f.read(4)
    toc = struct.unpack("<i", s)[0]

    metadata = {}    
    for prop in tocProperties.keys():
        metadata[prop] = (toc & tocProperties[prop])!=0
        
    #print ("TOC: "+toc)
    # Contents type (bit mask not yet decoded)


    # The version number
    s = f.read(4)
    version = struct.unpack("<i", s)[0]

    
    s = f.read(16)
    (next_segment_offset,raw_data_offset) = struct.unpack("<QQ", s)
    #print ("Length remaining: "+str(length_remaining))


    #print ("Length meta: "+str(length_meta))


    return (metadata,version,next_segment_offset,raw_data_offset)






def readObject( f ):
    """
    Read object in the metadata array
    """

    # Read the object path
    s = f.read(4)
    lnth = struct.unpack("<L", s)[0]
    objectpath = f.read(lnth)
    
        
    s = f.read(4)
    rawdataindex = struct.unpack("<L", s)[0]
    
    # No raw data associated
    if   (rawdataindex==0xFFFFFFFF):
        rawdata=()

    # Raw data index same as before
    elif (rawdataindex==0x00000000):
        rawdata = object_rawdata[objectpath]

    else:

        #print "==>Raw data reading",byteToHex(s),",that is,",rawdataindex,"bytes"

        #s = f.read(rawdataindex)

        # New raw data index!

        inf_length = rawdataindex
        
        # DataType
        s = f.read(4)
        rawdata_datatype = dataTypeFrom(s)
        
        # Dimension of the raw data array
        s = f.read(4)
        #print "Dimension: ",byteToHex(s)
        rawdata_dim = struct.unpack("<L", s)[0]


        
        # Number of raw data values
        s = f.read(8)
        rawdata_values = struct.unpack("<Q", s)[0]
            
        rawdata=(
            rawdata_datatype,
            rawdata_dim,
            rawdata_values
            )
        object_rawdata[objectpath] = rawdata

        #print "==>Done reading raw data:",rawdata

        
        
        
    # Read the number of properties
    s = f.read(4)
    nProp = struct.unpack("<L", s)[0]
    #print "Has",nProp,"properties"

    properties = {}
    for j in range(0,nProp):

        #print "Property",j
        # Read one property
        
        # Read the property name
        s = f.read(4)
        numb = struct.unpack("<L", s)[0]
        name = f.read(numb)
        #print name
        
        
        # Read the data type
        s = f.read(4)
        #print "Data type",s,byteToHex(s)
        datatype = dataTypeFrom(s)
        

        value = ''

        # If it's a string, read the length
        if (datatype=='tdsTypeString'):
            s = f.read(4)
            lengte = struct.unpack("<L", s)[0]
            value = f.read(lengte)
            
        else:
            nm = dataTypeLength( datatype )
            
            s = f.read(nm)
            value = getValue( s, "<", datatype )
            
            
        properties[name]=(datatype,value)



    return (objectpath,
            rawdataindex,
            rawdata,
            properties)






def mergeProperties( prop, newprop ):
    """
    Merge the two property lists, using the newprop
    list to overwrite if conflicts arise.
    """
    
    # What we will return
    retprop = prop

    # Now we change the values wherever we need to
    for k in newprop.keys():
        retprop[k]=newprop[k]

    # And the return the merged list
    return retprop





def mergeObject( obj, newobj ):
    """
    Ok, we are given two objects: obj and alt.
    We make all the changes (new values or
    overwriting old values), taking newobj as
    dominant.
    """

    (objectpath,
     rawdataindex,
     rawdata,
     properties) = obj

    (newobjectpath,
     newrawdataindex,
     newrawdata,
     newproperties) = newobj


    # We assume that objectpath is the same
    if (newobjectpath!=objectpath):
        print("Error: trying to merge non-same objectpaths:",newobjectpath,objectpath)
        exit()


    # If there is some change in the raw data associated
    if (not (newrawdataindex in [0xFFFFFFFF,0x00000000])):
        retrawdataindex = newrawdataindex
        retrawdata      = newrawdata
    else:
        retrawdataindex = rawdataindex
        retrawdata      = rawdata


    return (objectpath,
            retrawdataindex,
            retrawdata,
            mergeProperties(properties,newproperties))

    



def mergeObjects( objects, newobjects ):
    """
    Return the objects (metadata), but
    add the stuff that is in newobjects.
    """
    retobjects = objects

    # For all the new objects...
    for obj in newobjects.keys():

        # See if there is an old version already
        if (obj in retobjects.keys()):

            # Then update the old version using the new information
            retobjects[obj] = mergeObject(retobjects[obj],newobjects[obj])
        else:

            # Else just add it anew
            retobjects[obj] = newobjects[obj]

    return retobjects








def readMetaData( f ):
    """
    Read meta data from file f.
    
    We return (objects,objectorder) where
    objects is the structure containing all information about
    objects, and objectorder is a list of objectpaths (object ID's if you want)
    in the order that they have been presented. We need this
    later when we start reading the raw data, since it then comes
    in this very order.
    """

    # The number of objects in this metadata
    s = f.read(4)
    nObjects = struct.unpack("<l", s)[0]

    
    objects     = {}
    objectorder = []

    for i in range(0,nObjects):

        obj = readObject(f)

        (objectpath,
         rawdataindex,
         rawdata,
         properties) = obj

        if verbose:
            print("Read object",objectpath)

        # Add this object, or, if an object with the same objectpath
        # exists already, make it update that one.
        if (objectpath in objects.keys()):
            objects[objectpath] = mergeObjects(objects[objectpath],obj)
        else:
            # We add it anew
            objects[objectpath] = obj
            objectorder.append( objectpath )

        


    return (objects,objectorder)





def isChannel(obj):
    """
    Tell us whether the given object is a channel
    (in the current segment) and if so, returns
    the meta information about the raw data.
    """
    (_,rawdataindex,_,_) = obj
    return rawdataindex!=0xFFFFFFFF









def readRawData( f, leadin, segmentobjects, objectorder, filesize ):
    """
    Read raw data from file f,
    given the previously read leadin.
    segmentobjects are the objects that are given in this segment.
    Objectorder is a list of objectpaths (object id's) that shows
    the order in which the objects are given in the metadata. 
    That is important, for that will be the order in which their
    raw data needs to be read.
    """

    (metadata,version,next_segment_offset,raw_data_offset) = leadin

    # Whether the channel data is interleaved
    interleaved = metadata["kTocInterleavedData"]

    # Set the correct endianness (still need to check this!)
    endianness = '<'
    if metadata['kTocBigEndian']: endianness = '>'



    # First see which objects are channels (or really
    # actually which objects are channels AND have data in this segment.
    channel_sizes = {}
    channels = [ obj for obj in objectorder if isChannel(segmentobjects[obj]) ]


    for c in channels:
        channel = segmentobjects[c]

        (name,rawdataindex,rawdata,values)=channel
        
        (rawdata_datatype, rawdata_dim, rawdata_values) = rawdata

        if (rawdata_dim!=1):
            print("Error! Raw data dimension is ",rawdata_dim," and should have been 1.")
            exit()
        
        # Calculate how many bytes a single value is
        datapointsize= dataTypeLength(rawdata_datatype)
        
        # Array dimension (should really be 1)
        channel_size = datapointsize * rawdata_dim * rawdata_values
        
        channel_sizes[c] = channel_size
        

        
    # How much data in all channels together
    chunk_size = sum([ channel_sizes[c] for c in channels ])


    # A correction given on the TDMS specification website
    if next_segment_offset==-1:
        next_segment_offset=filesize

    # Raw data size of total chunks
    # (next_segment_offset should already have been corrected if -1)
    total_chunks = next_segment_offset - raw_data_offset
    # Hm, I think this quantity should be the total data
    # in this segment.

    # Hack by dlr: handle cases where file reports that there's raw
    # data of size 0.
    if total_chunks == 0:
        n_chunks = 0
    else:
        n_chunks = total_chunks // chunk_size
    
        if (total_chunks % chunk_size) != 0:
            raise ValueError("Data size is not a multiple of the chunk size")
    # end if...else, end of meddling by dlr.
    
    
    if verbose:
        print("Ready for reading",total_chunks,"bytes (",chunk_size, ") in",n_chunks,"chunks")

    
    # Initialise data to be empty
    data = {}
    for c in channels:
        (_, _, (datatype, _, _), values) = segmentobjects[c]
        data[c] = array.array(tdsDataTypesTranscriptions[datatype])
    
    if interleaved:
        if verbose:
            print(" ==> Interleaved")
            
        j=0
        while j<chunk_size:
            for c in channel:
                data[c].fromfile(f, 1)
            j+=1
    else:
        if verbose:
            print(" ==> Not Interleaved")
            
        for chunk in range(n_chunks):
            for c in channels:
                size= channel_sizes[c]
                (name,
                 rawdataindex,
                 (datatype, rawdata_dim, rawdata_values),
                 values) = segmentobjects[c]
                 
                data[c].fromfile(f, rawdata_values)

    file10 = struct.unpack(endianness + 'h', b'\1\0')
    host10 = struct.unpack('=h', b'\1\0')
    
    if file10 != host10:
       for c in channels:
          data[c].byteswap()

    return data









def mergeRawData( rawdata, newrawdata ):
    """
    Return the raw data, appended the new
    raw data.
    """
    for channel in newrawdata.keys():

        # If we already had data on this channel
        if (channel in rawdata.keys()):
            rawdata[channel].extend(newrawdata[channel])

        # Else we just chart it annew
        else:
            rawdata[channel] = newrawdata[channel]
    return rawdata

    







def readSegment( f, filesize, data ):
    """
    Read a segment from file f, whose filesize is given,
    and data is what we have read already
    """

    # This is the data we have so far.
    # The stuff in this segment is going to append to this.
    (objects,rawdata)=data


    leadin = readLeadIn(f)
    (metadata,version,next_segment_offset,raw_data_offset) = leadin


    newobjects = {}
    # If the segment has metadata...
    if (metadata["kTocMetaData"]):

        # Read the meta data
        (newobjects,newobjectorder) = readMetaData(f)

        # Merge the new information with what we knew already about the objects.
        objects = mergeObjects( objects, newobjects )



    if (metadata["kTocRawData"]):

        # Read the raw data
        newdata = readRawData(f,leadin,newobjects,newobjectorder,filesize)

        # And merge the data we just read with what we knew already
        rawdata = mergeRawData( rawdata, newdata )
        

    return (objects,rawdata)







def dumpProperties(props):
    ret = ''
    for pr in props:
        (tp,val)=props[pr]
        ret = ret + (pr+'=') + str(val) + ", "
    return ret



def csvDump(objects,data):
    """
    Dump the (objects,rawdata) that we read from a TDMS file
    straight into a CSV file.
    """

    ret = ''
    for obj in objects.keys():

        # Objects
        (objectpath,
         rawdataindex,
         rawdata,
         properties) = objects[obj]
        
        print ("OBJECT "+objectpath+" ("+dumpProperties(properties)+")\n")
        # ret = ret + ''

    i = 0
    maxi = max([ len(data[obj]) for obj in objects.keys() if obj in data.keys() ])

    channels = [ obj for obj in objects.keys() if isChannel(objects[obj]) ]
    ret += '\t'.join(channels)+'\n'

    for i in range(maxi):
        
        for obj in channels:

            val = ''
            if ((obj in data.keys()) and i<len(data[obj])):
                val = str(data[obj][i])
                # The raw data associated with the object
        
            ret += val+"\t"

        ret += "\n"

    return ret









def addTimeTrack( obj, channel ):
    """
    Ok, so we've read the data. Now it's possible that we require some post-processing. For example, if at least one track has time-data set, we'll add a corresponding time vector.

    So channel is the channel for which we want to have the time vector.
    And object contains its meta data.

    We return False if we can't find time data
    
    """

    # Now check for each object whether it has 
    (objectpath, rawdataindex, rawdata, properties) = obj

    if (
        # If we have time-data for this track
        'wf_increment'     in properties.keys() and
        'wf_start_offset'  in properties.keys()
        ):

        (_,incr)   = properties['wf_increment']
        (_,offset) = properties['wf_start_offset']

        

        # Then build the time track
        timetrack = [ offset+(i*incr) for i in range(0,len(channel)) ]
        return timetrack


    # Else we can't find time data
    return False
    







def read( filename ):
    """
    Reads TDMS file with the given filename.
    We return the data, which is, object meta data and raw channel data.

    Notice that we do not read the (optionally) accompanying .tdms_index
    since it is supposed to be an exact copy of the .tdms file, without the
    raw data. So it should contain nothing new.
    """



    # We start with empty data
    data = ({},{})

    


    # Then we read the data from a file, and return that
    f = open(filename, "rb")  # Open in binary mode for portability
    sz = os.path.getsize(filename)


    
    # While there's still something left to read
    while f.tell()<sz:

        # Now we read segment by segment
        data = readSegment(f,sz,data)

    f.close()





    return data







