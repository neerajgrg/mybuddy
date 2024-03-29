
# def list_assets(self, collection_name: str):
#     request = (
#         EmeraldRequest.builder()
#         .set_env(stage=self.is_stage)
#         .set_token_provider(self.token_provider)
#         .build()
#     )
#     response = await request.invoke('/collection/' + collection_name + '/assets', data={}, method="get")
#     return response