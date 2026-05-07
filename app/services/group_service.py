from app.core.db import handle_response
from app.core.supabase import supabase
from fastapi import HTTPException, status
from app.utils.logger import sys_logger
from app.core.security import verify_group_membership

def create_group(user_id: str, name: str):
    sys_logger.info(f"Creating group | user={user_id} | name={name}")
    res = supabase.rpc("create_group_with_admin", {
        "p_name"   : name,
        "p_user_id": user_id
    }).execute()

    data = handle_response(res)

    group = data[0]

    sys_logger.info(f"Group {name} create by {user_id}")
    return group

def request_to_join(user_id:str, group_id: str):
    sys_logger.info(f"Join request | user={user_id} | group={group_id}")

    try:
        res = supabase.table("group_join_requests").insert({
            "group_id": group_id,
            "user_id": user_id,
            "status": "PENDING"
        }).execute()
        handle_response(res)

        return {
            "status": "requested"
        }
    except Exception as e:
        if e.message and 'duplicate' in e.message.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already have a pending request")

def approve_join_request(admin_id: str, request_id: str):
    sys_logger.info(f"Approve request | admin={admin_id} | request_id={request_id}")

    res = supabase.table("group_join_requests").select("*").eq("id", request_id).single().execute()

    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    req = res.data

    role = verify_group_membership(admin_id, group_id=req["group_id"], require_admin=True)

    if not role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if req["status"] != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request already processed")

    insert_res = supabase.table("group_members").insert({
        "group_id": req["group_id"],
        "user_id" : req["user_id"],
        "role"    : "member"
    }).execute()

    if not insert_res:
        sys_logger.error(f"Member insert failed: {insert_res}")
        raise HTTPException(status_code=400, detail="Failed to add member")

    supabase.table("group_join_requests").update({
        "status": "APPROVED"
    }).eq("id", request_id).execute()

    sys_logger.info(f"User {req["user_id"]} approved by {admin_id}")

    return {
        "status": "approved"
    }


def reject_join_request(admin_id: str, request_id: str):
    sys_logger.info(f"Approve request | admin={admin_id} | request_id={request_id}")

    res = supabase.table("group_join_requests").select("*").eq("id", request_id).single().execute()

    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    req = res.data

    role = verify_group_membership(admin_id, group_id=req["group_id"], require_admin=True)

    if not role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if req["status"] != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request already processed")



    supabase.table("group_join_requests").update({
        "status": "REJECTED"
    }).eq("id", request_id).execute()

    sys_logger.info(f"User {req["user_id"]} rejected by {admin_id}")

    return {
        "status": "rejected"
    }

def get_user_groups(user_id: str):
    res = supabase.rpc("get_user_groups", {
        "p_user_id": user_id
    }).execute()

    data = handle_response(res)

    return data

def get_pending_join_requests(group_id: str):
    res = supabase.table("group_join_requests").select("*, profiles(name)").eq("group_id", group_id).eq("status", "PENDING").execute()

    data = handle_response(res)

    return data

def search_groups(user_id: str, query: str):
    sys_logger.info(f"Search groups | user={user_id} | query={query}")

    res = supabase.rpc("search_groups", {
        "p_search": query,
        "p_user_id": user_id
    }).execute()

    return handle_response(res)

def group_members(group_id: str, role: str):
    res = supabase.table("group_members").select("*, profiles(name)").eq("group_id", group_id).execute()
    is_admin = False
    if role == "admin":
        is_admin = True
    data = handle_response(res)
    return {"is_admin": is_admin, "data": data}

def group_info(group_id: str, role: str):
    mem_res        = supabase.table("group_members").select("*, profiles(name)").eq("group_id", group_id).execute()
    mem_shares_res = supabase.rpc("get_user_share_percentage",{
        "target_group_id": group_id
    }).execute()

    mem_shares = handle_response(mem_shares_res)    

    is_admin = False
    if role == "admin":
        is_admin = True
    mem_data = handle_response(mem_res)
    shares_lookup = {item['user_id']: item['percentage_share'] for item in mem_shares}

    for member in mem_data:
        # use .get() to avoid errors if a user_id is missing in the first list
        member['percentage_share'] = shares_lookup.get(member['user_id'], 0)
    group_res = supabase.table("groups").select("id, name").eq("id", group_id).single().execute()
    group_data = handle_response(group_res)

    return {
        "is_admin": is_admin,
        "members" : mem_data,
        "about"   : group_data
    }
