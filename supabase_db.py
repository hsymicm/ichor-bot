# import os
# from supabase import create_client

# key = os.environ['supabaseKEY']
# url = os.environ['supabaseURL']


# class SupabaseDB():
#     def __init__(self):
#         self.supabase = create_client(url, key)

#     def getInventory(self, id):
#         data = self.supabase.rpc('get_inventory', {"uid": id}).execute()
#         return data.data

#     def updateInventory(self, id, arr):
#         self.supabase.rpc('update_inventory', {
#             "uid": id,
#             "updated_arr": arr
#         }).execute()

#     def setUserWatchList(self, id, element):
#         self.supabase.rpc('insert_data', {
#             "new_element": element,
#             "uid": id,
#         }).execute()

#     def delUserWatchList(self, id, element):
#         self.supabase.rpc('remove_data', {
#             "element": element,
#             "uid": id,
#         }).execute()

#     def getUserWatchList(self, id):
#         data = self.supabase.table("otakuTable").select("watch_list").eq(
#             "user_id", id).execute()
#         return data.data[0]['watch_list'] if len(data.data) > 0 else None

#     def getUserList(self):
#         data = self.supabase.table("otakuTable").select("user_id").execute()
#         return [user['user_id']
#                 for user in data.data] if len(data.data) > 0 else None
