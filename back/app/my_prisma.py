# from prisma import Client
# from datetime import datetime
# from prisma.errors import ClientNotConnectedError

# client = Client()

# async def save_recommendation(recommendation):
#     try:
#         # データベースに接続されていなければ接続
#         if not client.is_connected():
#             print("データベースに接続されていません。接続を試みます...")
#             await client.connect()
#             print("データベースへの接続が確立されました。")

#         result = await client.recommendation.create({
#             'user_id': recommendation.user_id,
#             'company': recommendation.company,
#             'activity_type': recommendation.activity_type,
#             'recommend_station': recommendation.recommend_station,
#             'recommend_details': recommendation.recommend_details,
#             # 'created_at': datetime.now()
#         })
#         print("推薦情報が正常に保存されました。")

#         return result
#     except ClientNotConnectedError:
#         print("ClientNotConnectedErrorが発生しました。再接続を試みます...")
#         # print(f"ClientErrorが発生しました: {e}")
#         # print("再接続を試みます...")
#         await client.connect()
#         return await save_recommendation(recommendation)  # 再試行
    
#     except Exception as e:
#         # エラーハンドリングを適切に行う
#         print(f"Error saving recommendation: {e}")
#         raise e
    
#     finally:
#         await client.disconnect()  # 使用後は切断
#         print("データベースの接続を閉じました。")

