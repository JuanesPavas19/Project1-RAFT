# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import service_pb2 as service__pb2

GRPC_GENERATED_VERSION = '1.66.1'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in service_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class DatabaseServiceStub(object):
    """Servicio para la BD y Raft
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ReadData = channel.unary_unary(
                '/database.DatabaseService/ReadData',
                request_serializer=service__pb2.ReadRequest.SerializeToString,
                response_deserializer=service__pb2.ReadResponse.FromString,
                _registered_method=True)
        self.WriteData = channel.unary_unary(
                '/database.DatabaseService/WriteData',
                request_serializer=service__pb2.WriteRequest.SerializeToString,
                response_deserializer=service__pb2.WriteResponse.FromString,
                _registered_method=True)
        self.RequestVote = channel.unary_unary(
                '/database.DatabaseService/RequestVote',
                request_serializer=service__pb2.VoteRequest.SerializeToString,
                response_deserializer=service__pb2.VoteResponse.FromString,
                _registered_method=True)
        self.AppendEntries = channel.unary_unary(
                '/database.DatabaseService/AppendEntries',
                request_serializer=service__pb2.AppendEntriesRequest.SerializeToString,
                response_deserializer=service__pb2.AppendEntriesResponse.FromString,
                _registered_method=True)
        self.Ping = channel.unary_unary(
                '/database.DatabaseService/Ping',
                request_serializer=service__pb2.PingRequest.SerializeToString,
                response_deserializer=service__pb2.PingResponse.FromString,
                _registered_method=True)
        self.UpdateActiveNodes = channel.unary_unary(
                '/database.DatabaseService/UpdateActiveNodes',
                request_serializer=service__pb2.UpdateRequest.SerializeToString,
                response_deserializer=service__pb2.UpdateResponse.FromString,
                _registered_method=True)
        self.DegradeToFollower = channel.unary_unary(
                '/database.DatabaseService/DegradeToFollower',
                request_serializer=service__pb2.DegradeRequest.SerializeToString,
                response_deserializer=service__pb2.DegradeResponse.FromString,
                _registered_method=True)
        self.ReplicateData = channel.unary_unary(
                '/database.DatabaseService/ReplicateData',
                request_serializer=service__pb2.WriteRequest.SerializeToString,
                response_deserializer=service__pb2.WriteResponse.FromString,
                _registered_method=True)
        self.RequestLeader = channel.unary_unary(
                '/database.DatabaseService/RequestLeader',
                request_serializer=service__pb2.LeaderRequest.SerializeToString,
                response_deserializer=service__pb2.LeaderResponse.FromString,
                _registered_method=True)
        self.RequestDatabase = channel.unary_unary(
                '/database.DatabaseService/RequestDatabase',
                request_serializer=service__pb2.DatabaseRequest.SerializeToString,
                response_deserializer=service__pb2.DatabaseResponse.FromString,
                _registered_method=True)


class DatabaseServiceServicer(object):
    """Servicio para la BD y Raft
    """

    def ReadData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def WriteData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RequestVote(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AppendEntries(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Ping(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateActiveNodes(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DegradeToFollower(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReplicateData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RequestLeader(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RequestDatabase(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_DatabaseServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ReadData': grpc.unary_unary_rpc_method_handler(
                    servicer.ReadData,
                    request_deserializer=service__pb2.ReadRequest.FromString,
                    response_serializer=service__pb2.ReadResponse.SerializeToString,
            ),
            'WriteData': grpc.unary_unary_rpc_method_handler(
                    servicer.WriteData,
                    request_deserializer=service__pb2.WriteRequest.FromString,
                    response_serializer=service__pb2.WriteResponse.SerializeToString,
            ),
            'RequestVote': grpc.unary_unary_rpc_method_handler(
                    servicer.RequestVote,
                    request_deserializer=service__pb2.VoteRequest.FromString,
                    response_serializer=service__pb2.VoteResponse.SerializeToString,
            ),
            'AppendEntries': grpc.unary_unary_rpc_method_handler(
                    servicer.AppendEntries,
                    request_deserializer=service__pb2.AppendEntriesRequest.FromString,
                    response_serializer=service__pb2.AppendEntriesResponse.SerializeToString,
            ),
            'Ping': grpc.unary_unary_rpc_method_handler(
                    servicer.Ping,
                    request_deserializer=service__pb2.PingRequest.FromString,
                    response_serializer=service__pb2.PingResponse.SerializeToString,
            ),
            'UpdateActiveNodes': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateActiveNodes,
                    request_deserializer=service__pb2.UpdateRequest.FromString,
                    response_serializer=service__pb2.UpdateResponse.SerializeToString,
            ),
            'DegradeToFollower': grpc.unary_unary_rpc_method_handler(
                    servicer.DegradeToFollower,
                    request_deserializer=service__pb2.DegradeRequest.FromString,
                    response_serializer=service__pb2.DegradeResponse.SerializeToString,
            ),
            'ReplicateData': grpc.unary_unary_rpc_method_handler(
                    servicer.ReplicateData,
                    request_deserializer=service__pb2.WriteRequest.FromString,
                    response_serializer=service__pb2.WriteResponse.SerializeToString,
            ),
            'RequestLeader': grpc.unary_unary_rpc_method_handler(
                    servicer.RequestLeader,
                    request_deserializer=service__pb2.LeaderRequest.FromString,
                    response_serializer=service__pb2.LeaderResponse.SerializeToString,
            ),
            'RequestDatabase': grpc.unary_unary_rpc_method_handler(
                    servicer.RequestDatabase,
                    request_deserializer=service__pb2.DatabaseRequest.FromString,
                    response_serializer=service__pb2.DatabaseResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'database.DatabaseService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('database.DatabaseService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class DatabaseService(object):
    """Servicio para la BD y Raft
    """

    @staticmethod
    def ReadData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/database.DatabaseService/ReadData',
            service__pb2.ReadRequest.SerializeToString,
            service__pb2.ReadResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def WriteData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/database.DatabaseService/WriteData',
            service__pb2.WriteRequest.SerializeToString,
            service__pb2.WriteResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def RequestVote(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/database.DatabaseService/RequestVote',
            service__pb2.VoteRequest.SerializeToString,
            service__pb2.VoteResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def AppendEntries(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/database.DatabaseService/AppendEntries',
            service__pb2.AppendEntriesRequest.SerializeToString,
            service__pb2.AppendEntriesResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Ping(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/database.DatabaseService/Ping',
            service__pb2.PingRequest.SerializeToString,
            service__pb2.PingResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UpdateActiveNodes(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/database.DatabaseService/UpdateActiveNodes',
            service__pb2.UpdateRequest.SerializeToString,
            service__pb2.UpdateResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def DegradeToFollower(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/database.DatabaseService/DegradeToFollower',
            service__pb2.DegradeRequest.SerializeToString,
            service__pb2.DegradeResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ReplicateData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/database.DatabaseService/ReplicateData',
            service__pb2.WriteRequest.SerializeToString,
            service__pb2.WriteResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def RequestLeader(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/database.DatabaseService/RequestLeader',
            service__pb2.LeaderRequest.SerializeToString,
            service__pb2.LeaderResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def RequestDatabase(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/database.DatabaseService/RequestDatabase',
            service__pb2.DatabaseRequest.SerializeToString,
            service__pb2.DatabaseResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
