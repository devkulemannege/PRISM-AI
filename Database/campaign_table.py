import connect_db
connection, cont = connect_db.connection()

def addRow(businessId, name, prompt, template, parameters, targetProblem, targetAudience, 
           uniqueSolution, whyNeeded, mainBenefits, socialProof, price, 
           offer, urgency, cta):
    '''function which adds data to 
    product table of database'''

    colNames = 'businessId, campaignNme, prompt, template, parameters, targetProblem, targetAudience, ' \
    'uniqueSolution, whyNeeded, mainBenefits, socialProof, price, offer, urgency, cta' # column names 
    try:
        cont.execute(f"INSERT INTO campaign ({colNames}) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (int(businessId[0][0]), name, prompt, template, parameters, targetProblem, targetAudience, 
                uniqueSolution, whyNeeded, mainBenefits, socialProof, price, 
                offer, urgency, cta))
    except Exception as error:
        raise Exception(f'Error location: campaign_table.py | Detailed: {error}') # error identification

    connection.commit()
    connection.close()


# below code is for debugging purposes
'''
businessId = [(3,)]
name = "GreenSprout Plant Kit"
template = "Gardening Product Landing Page"
targetProblem = "Difficulty in growing plants at home"
targetAudience = "Urban gardeners, plant enthusiasts, and eco-friendly homeowners"
uniqueSolution = "Complete, easy-to-use plant growth kit with organic seeds and self-watering pots"
whyNeeded = "To make home gardening simple and enjoyable"
mainBenefits = "Low maintenance, space-saving, and eco-friendly"
socialProof = "Loved by over 10,000 happy plant parents"
price = '49.99'
offer = "Free shipping for orders over $50"
urgency = "Limited edition kits available"
cta = "Get Yours Now"

addRow(
    businessId,
    name,
    template,
    targetProblem,
    targetAudience,
    uniqueSolution,
    whyNeeded,
    mainBenefits,
    socialProof,
    price,
    offer,
    urgency,
    cta
)
'''
