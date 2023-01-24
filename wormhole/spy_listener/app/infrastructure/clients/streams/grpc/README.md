# GRPC Directory

This directory contains the protobuf-compiled code (translated to python) that's necessary for a gRPC service. 

The package, [grpcio-tools](https://pypi.org/project/grpcio-tools/), was used to generate thesse files, taking .proto files as inputs.

**Example Usage**:
First, `cd` into the `grpc` directory. Then, run:
```
python -m grpc_tools.protoc -I./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/helloworld.proto
```