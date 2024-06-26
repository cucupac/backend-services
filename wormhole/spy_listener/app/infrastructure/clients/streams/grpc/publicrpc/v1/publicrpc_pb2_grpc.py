# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from publicrpc.v1 import publicrpc_pb2 as publicrpc_dot_v1_dot_publicrpc__pb2


class PublicRPCServiceStub(object):
    """PublicRPCService service exposes endpoints to be consumed externally; GUIs, historical record keeping, etc."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetLastHeartbeats = channel.unary_unary(
            "/publicrpc.v1.PublicRPCService/GetLastHeartbeats",
            request_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetLastHeartbeatsRequest.SerializeToString,
            response_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetLastHeartbeatsResponse.FromString,
        )
        self.GetSignedVAA = channel.unary_unary(
            "/publicrpc.v1.PublicRPCService/GetSignedVAA",
            request_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetSignedVAARequest.SerializeToString,
            response_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetSignedVAAResponse.FromString,
        )
        self.GetSignedBatchVAA = channel.unary_unary(
            "/publicrpc.v1.PublicRPCService/GetSignedBatchVAA",
            request_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetSignedBatchVAARequest.SerializeToString,
            response_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetSignedBatchVAAResponse.FromString,
        )
        self.GetCurrentGuardianSet = channel.unary_unary(
            "/publicrpc.v1.PublicRPCService/GetCurrentGuardianSet",
            request_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetCurrentGuardianSetRequest.SerializeToString,
            response_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetCurrentGuardianSetResponse.FromString,
        )
        self.GovernorGetAvailableNotionalByChain = channel.unary_unary(
            "/publicrpc.v1.PublicRPCService/GovernorGetAvailableNotionalByChain",
            request_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetAvailableNotionalByChainRequest.SerializeToString,
            response_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetAvailableNotionalByChainResponse.FromString,
        )
        self.GovernorGetEnqueuedVAAs = channel.unary_unary(
            "/publicrpc.v1.PublicRPCService/GovernorGetEnqueuedVAAs",
            request_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetEnqueuedVAAsRequest.SerializeToString,
            response_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetEnqueuedVAAsResponse.FromString,
        )
        self.GovernorIsVAAEnqueued = channel.unary_unary(
            "/publicrpc.v1.PublicRPCService/GovernorIsVAAEnqueued",
            request_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorIsVAAEnqueuedRequest.SerializeToString,
            response_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorIsVAAEnqueuedResponse.FromString,
        )
        self.GovernorGetTokenList = channel.unary_unary(
            "/publicrpc.v1.PublicRPCService/GovernorGetTokenList",
            request_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetTokenListRequest.SerializeToString,
            response_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetTokenListResponse.FromString,
        )


class PublicRPCServiceServicer(object):
    """PublicRPCService service exposes endpoints to be consumed externally; GUIs, historical record keeping, etc."""

    def GetLastHeartbeats(self, request, context):
        """GetLastHeartbeats returns the last heartbeat received for each guardian node in the
        node's active guardian set. Heartbeats received by nodes not in the guardian set are ignored.
        The heartbeat value is null if no heartbeat has yet been received.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetSignedVAA(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetSignedBatchVAA(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetCurrentGuardianSet(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GovernorGetAvailableNotionalByChain(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GovernorGetEnqueuedVAAs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GovernorIsVAAEnqueued(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GovernorGetTokenList(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_PublicRPCServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetLastHeartbeats": grpc.unary_unary_rpc_method_handler(
            servicer.GetLastHeartbeats,
            request_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetLastHeartbeatsRequest.FromString,
            response_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetLastHeartbeatsResponse.SerializeToString,
        ),
        "GetSignedVAA": grpc.unary_unary_rpc_method_handler(
            servicer.GetSignedVAA,
            request_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetSignedVAARequest.FromString,
            response_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetSignedVAAResponse.SerializeToString,
        ),
        "GetSignedBatchVAA": grpc.unary_unary_rpc_method_handler(
            servicer.GetSignedBatchVAA,
            request_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetSignedBatchVAARequest.FromString,
            response_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetSignedBatchVAAResponse.SerializeToString,
        ),
        "GetCurrentGuardianSet": grpc.unary_unary_rpc_method_handler(
            servicer.GetCurrentGuardianSet,
            request_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetCurrentGuardianSetRequest.FromString,
            response_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GetCurrentGuardianSetResponse.SerializeToString,
        ),
        "GovernorGetAvailableNotionalByChain": grpc.unary_unary_rpc_method_handler(
            servicer.GovernorGetAvailableNotionalByChain,
            request_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetAvailableNotionalByChainRequest.FromString,
            response_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetAvailableNotionalByChainResponse.SerializeToString,
        ),
        "GovernorGetEnqueuedVAAs": grpc.unary_unary_rpc_method_handler(
            servicer.GovernorGetEnqueuedVAAs,
            request_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetEnqueuedVAAsRequest.FromString,
            response_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetEnqueuedVAAsResponse.SerializeToString,
        ),
        "GovernorIsVAAEnqueued": grpc.unary_unary_rpc_method_handler(
            servicer.GovernorIsVAAEnqueued,
            request_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorIsVAAEnqueuedRequest.FromString,
            response_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorIsVAAEnqueuedResponse.SerializeToString,
        ),
        "GovernorGetTokenList": grpc.unary_unary_rpc_method_handler(
            servicer.GovernorGetTokenList,
            request_deserializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetTokenListRequest.FromString,
            response_serializer=publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetTokenListResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "publicrpc.v1.PublicRPCService", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class PublicRPCService(object):
    """PublicRPCService service exposes endpoints to be consumed externally; GUIs, historical record keeping, etc."""

    @staticmethod
    def GetLastHeartbeats(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/publicrpc.v1.PublicRPCService/GetLastHeartbeats",
            publicrpc_dot_v1_dot_publicrpc__pb2.GetLastHeartbeatsRequest.SerializeToString,
            publicrpc_dot_v1_dot_publicrpc__pb2.GetLastHeartbeatsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetSignedVAA(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/publicrpc.v1.PublicRPCService/GetSignedVAA",
            publicrpc_dot_v1_dot_publicrpc__pb2.GetSignedVAARequest.SerializeToString,
            publicrpc_dot_v1_dot_publicrpc__pb2.GetSignedVAAResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetSignedBatchVAA(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/publicrpc.v1.PublicRPCService/GetSignedBatchVAA",
            publicrpc_dot_v1_dot_publicrpc__pb2.GetSignedBatchVAARequest.SerializeToString,
            publicrpc_dot_v1_dot_publicrpc__pb2.GetSignedBatchVAAResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetCurrentGuardianSet(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/publicrpc.v1.PublicRPCService/GetCurrentGuardianSet",
            publicrpc_dot_v1_dot_publicrpc__pb2.GetCurrentGuardianSetRequest.SerializeToString,
            publicrpc_dot_v1_dot_publicrpc__pb2.GetCurrentGuardianSetResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GovernorGetAvailableNotionalByChain(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/publicrpc.v1.PublicRPCService/GovernorGetAvailableNotionalByChain",
            publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetAvailableNotionalByChainRequest.SerializeToString,
            publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetAvailableNotionalByChainResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GovernorGetEnqueuedVAAs(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/publicrpc.v1.PublicRPCService/GovernorGetEnqueuedVAAs",
            publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetEnqueuedVAAsRequest.SerializeToString,
            publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetEnqueuedVAAsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GovernorIsVAAEnqueued(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/publicrpc.v1.PublicRPCService/GovernorIsVAAEnqueued",
            publicrpc_dot_v1_dot_publicrpc__pb2.GovernorIsVAAEnqueuedRequest.SerializeToString,
            publicrpc_dot_v1_dot_publicrpc__pb2.GovernorIsVAAEnqueuedResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GovernorGetTokenList(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/publicrpc.v1.PublicRPCService/GovernorGetTokenList",
            publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetTokenListRequest.SerializeToString,
            publicrpc_dot_v1_dot_publicrpc__pb2.GovernorGetTokenListResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
