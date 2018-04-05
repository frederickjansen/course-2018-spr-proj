import urllib.request
import json
import geojson
import dml
import prov.model
import datetime
import uuid

class getCOpenSpace(dml.Algorithm):
    contributor = 'cwsonn_levyjr'
    reads = []
    writes = ['cwsonn_levyjr.Copenspace']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('cwsonn_levyjr', 'cwsonn_levyjr')

        url = 'https://data.cambridgema.gov/resource/5ctr-ccas.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)

        repo.dropCollection("cwsonn_levyjr.Copenspace")
        repo.createCollection("cwsonn_levyjr.Copenspace")

        repo["cwsonn_levyjr.Copenspace"].insert_many(r)

#repo['cwsonn_levyjr.openspace'].metadata({'complete':True})

#print(repo['cwsonn_levyjr.openspace'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('cwsonn_levyjr', 'cwsonn_levyjr')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bod', 'https://data.cambridgema.gov/Planning/Open-Space/q73m-a5e2')
        
        #Agent
        this_script = doc.agent('alg:getCOpenSpace', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        #Resource
        resource = doc.entity('bod:2868d370c55d4d458d4ae2224ef8cddd_7', {'prov:label':'COpenSpaces', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'geojson'})
        
        #Activities
        this_run = doc.activity('log:a'+str(uuid.uuid4()), startTime, endTime,  {prov.model.PROV_TYPE:'ont:Retrieval'})
        
        #Usage
        doc.wasAssociatedWith(this_run, this_script)
        doc.used(this_run, resource, startTime)
        
        #New dataset
        open_space = doc.entity('dat:Copenspace', {prov.model.PROV_LABEL:'COpenSpaces', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(open_space, this_script)
        doc.wasGeneratedBy(open_space, this_run, endTime)
        doc.wasDerivedFrom(open_space, resource, this_run, this_run, this_run)
        
        repo.logout()
        
        return doc

'''getCOpenSpace.execute()
doc = getCOpenSpace.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))'''

## eof
