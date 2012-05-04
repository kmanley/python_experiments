import xhtml2pdf.pisa
import StringIO
import mako, mako.lookup

vars = {
    "date" : "August 22, 2011",
    "seller" : "Edward Weinstock & Elisa Field",
    "seller_address" : "103 Vails Lake Shore Drive, Brewster NY 10509",
    "buyer" : "Kevin Manley & Amy Pal",
    "buyer_address" : "20 Clayton Place, Ridgefield CT 06877",
    "address" : "20 Clayton Place, Ridgefield CT 06877",
    "lease_start_date" : "Sept 1, 2011",
    "lease_start_time" : "12:00",
    "lease_end_time" : "12:00",
    "lease_end_date" : "August 31, 2013",
    "required_closing_date" : "August 31, 2013",
    "option_ccy": "USD", 
    "option_premium": "20,000",
}

mylookup = mako.lookup.TemplateLookup(directories=['.'])
mytemplate = mylookup.get_template('contract_ct.html')
html = mytemplate.render(**vars)
infile = StringIO.StringIO(html)

#with file("contract_ct.html") as infile:
with file(r"test.pdf", "wb") as outfile:
    #pdf = xhtml2pdf.pisa.CreatePDF(StringIO.StringIO(html), outfile)
    pdf = xhtml2pdf.pisa.CreatePDF(infile, outfile)
    print pdf.err
#outfile.close()
#infile.close()
