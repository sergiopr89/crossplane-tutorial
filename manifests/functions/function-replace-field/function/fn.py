"""A Crossplane composition function."""

import re
import grpc
from crossplane.function import logging, resource, response
from crossplane.function.proto.v1 import run_function_pb2 as fnv1
from crossplane.function.proto.v1 import run_function_pb2_grpc as grpcv1


class FunctionRunner(grpcv1.FunctionRunnerService):
    """A FunctionRunner handles gRPC RunFunctionRequests."""

    def __init__(self):
        """Create a new FunctionRunner."""
        self.log = logging.get_logger()

    async def RunFunction(
        self, req: fnv1.RunFunctionRequest, _: grpc.aio.ServicerContext
    ) -> fnv1.RunFunctionResponse:
        """Run the function."""
        log = self.log.bind(tag=req.meta.tag)
        log.info("Running function")

        rsp = response.to(req)

        # get all the replaces in there
        replaces = req.input["replaces"]

        for replace in replaces:
            # For each replace, obtain the required inputs
            field_path = replace["fromPath"]
            pattern = replace["pattern"]
            value = replace["value"]

            # Locate the container in desired XR
            container = rsp.desired.composite.resource
            keys = field_path.split(".")
            for key in keys[:-1]:
                if key not in container:
                    container[key] = {}
                container = container[key]
            last_key = keys[-1]

            # Apply regex on the observed XR value and store in desired XR
            observed_value = req.observed.composite.resource
            for key in keys:
                observed_value = observed_value[key]
            # Apply value update
            container[last_key] = re.sub(pattern, value, str(observed_value))

        return rsp
