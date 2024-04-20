# from prisma import Client
# from datetime import datetime
# from prisma.errors import ClientNotConnectedError

# client = Client()

# async def save_recommendation(recommendation):
#     try:
#         # データベースに接続されていなければ接続
#         if not client.is_connected():
#             await client.connect()

#         result = await client.recommendation.create({
#             'user_id': recommendation.user_id,
#             'company': recommendation.company,
#             'activity_type': recommendation.activity_type,
#             'recommend_station': recommendation.recommend_station,
#             'recommend_details': recommendation.recommend_details,
#             'created_at': datetime.now()
#         })
#         return result
#     except ClientNotConnectedError:
#         await client.connect()
#         return await save_recommendation(recommendation)  # 再試行
#     except Exception as e:
#         # エラーハンドリングを適切に行う
#         print(f"Error saving recommendation: {e}")
#         raise e
#     finally:
#         await client.disconnect()  # 使用後は切断
