import numpy
def autocorr1(x):
    s = numpy.fft.fft(x)
    return numpy.real(numpy.fft.ifft(s*numpy.conjugate(s)))/numpy.var(x)

def autocorr2(x):
    result = numpy.correlate(x, x, mode='full')
    return result[result.size/2:]


x = numpy.array([float(x) for x in range(100)])
print autocorr1(x)
print "-" * 40
print autocorr2(x)
