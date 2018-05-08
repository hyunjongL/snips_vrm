# -*- coding: utf-8 -*-
from concurrent import futures
import time
import io
import json
import grpc
import nlu_pb2
import nlu_pb2_grpc
from snips_nlu import SnipsNLUEngine, load_resources
from snips_nlu.default_configs import CONFIG_EN

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


with io.open("dataset.json") as f:
    sample_dataset = json.load(f)

load_resources("ko")
snips_nlu_engine = SnipsNLUEngine()
snips_nlu_engine.fit(sample_dataset)

text = "나는"
parsing = snips_nlu_engine.parse(text)
print(json.dumps(parsing, indent=2))

class snips_server(nlu_pb2_grpc.snips_nluServicer):
  def nlu_engine(self, request, context):
    global snips_nlu_engine
    return nlu_pb2.nlu_response(intent=json.dumps(snips_nlu_engine.parse(request.utterance)))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    nlu_pb2_grpc.add_snips_nluServicer_to_server(snips_server(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
  serve()
