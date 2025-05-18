import aioboto3

class AWSClients:
    _session = None
    
    @classmethod
    def get_session(cls):
        if cls._session is None:
            cls._session = aioboto3.Session()
        return cls._session

    @classmethod
    async def get_ec2(cls, region):
        return cls.get_session().client('ec2', region_name=region)
    
    @classmethod 
    async def get_cloudwatch(cls, region):
        return cls.get_session().client('cloudwatch', region_name=region)