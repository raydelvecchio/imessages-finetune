# iMessage Finetune
Attempting to fine tune an LLM to sound like a user, fine tuned on all iMessages stored locally on Mac.

# Methodology
* To fine tune on a user's iMessages, we must first pre-process into a fine-tunable format
* We will select all non-group chat messages, constructing the LLM input format of messages where the "User" is the other person talking, for as many messages until we respect, and the "Assistant" is the user's response in the message
    * For example, if I have a chat with Alice that looks like this:
        ```
        {
            "Alice": "Hey, how are you?",
            "Me": "I'm doing well, thanks! How about you?",
            "Alice": "Not bad, just busy with work. Did you finish that project?",
            "Me": "Yes, I did! It was challenging but rewarding."
        }
        ```
    * The LLM input format would be:
        ```
        {
            "User": "Hey, how are you?",
            "Assistant": "I'm doing well, thanks! How about you?",
            "User": "Not bad, just busy with work. Did you finish that project?",
            "Assistant": "Yes, I did! It was challenging but rewarding."
        }
        ```
* Ideally, we should also detect links, and scrape them if we can, to best capture the context in which the user is responding

# iMessages Local Database

The iMessages database is stored locally on Mac as an SQLite database file:
* Location: `~/Library/Messages/chat.db`
* Format: SQLite

## Database Structure

Here's a detailed overview of the main tables and their columns:

1. **message**
   - ROWID (INTEGER)
   - guid (TEXT)
   - text (TEXT)
   - replace (INTEGER)
   - service_center (TEXT)
   - handle_id (INTEGER)
   - subject (TEXT)
   - country (TEXT)
   - attributedBody (BLOB)
   - version (INTEGER)
   - type (INTEGER)
   - service (TEXT)
   - account (TEXT)
   - account_guid (TEXT)
   - error (INTEGER)
   - date (INTEGER)
   - date_read (INTEGER)
   - date_delivered (INTEGER)
   - is_delivered (INTEGER)
   - is_finished (INTEGER)
   - is_emote (INTEGER)
   - is_from_me (INTEGER)
   - is_empty (INTEGER)
   - is_delayed (INTEGER)
   - is_auto_reply (INTEGER)
   - is_prepared (INTEGER)
   - is_read (INTEGER)
   - is_system_message (INTEGER)
   - is_sent (INTEGER)
   - has_dd_results (INTEGER)
   - is_service_message (INTEGER)
   - is_forward (INTEGER)
   - was_downgraded (INTEGER)
   - is_archive (INTEGER)
   - cache_has_attachments (INTEGER)
   - cache_roomnames (TEXT)
   - was_data_detected (INTEGER)
   - was_deduplicated (INTEGER)
   - is_audio_message (INTEGER)
   - is_played (INTEGER)
   - date_played (INTEGER)
   - item_type (INTEGER)
   - other_handle (INTEGER)
   - group_title (TEXT)
   - group_action_type (INTEGER)
   - share_status (INTEGER)
   - share_direction (INTEGER)
   - is_expirable (INTEGER)
   - expire_state (INTEGER)
   - message_action_type (INTEGER)
   - message_source (INTEGER)
   - associated_message_guid (TEXT)
   - associated_message_type (INTEGER)
   - balloon_bundle_id (TEXT)
   - payload_data (BLOB)
   - expressive_send_style_id (TEXT)
   - associated_message_range_location (INTEGER)
   - associated_message_range_length (INTEGER)
   - time_expressive_send_played (INTEGER)
   - message_summary_info (BLOB)
   - ck_sync_state (INTEGER)
   - ck_record_id (TEXT)
   - ck_record_change_tag (TEXT)
   - destination_caller_id (TEXT)
   - is_corrupt (INTEGER)
   - reply_to_guid (TEXT)
   - sort_id (INTEGER)
   - is_spam (INTEGER)
   - has_unseen_mention (INTEGER)
   - thread_originator_guid (TEXT)
   - thread_originator_part (TEXT)
   - syndication_ranges (TEXT)
   - synced_syndication_ranges (TEXT)
   - was_delivered_quietly (INTEGER)
   - did_notify_recipient (INTEGER)
   - date_retracted (INTEGER)
   - date_edited (INTEGER)
   - was_detonated (INTEGER)
   - part_count (INTEGER)
   - is_stewie (INTEGER)
   - is_kt_verified (INTEGER)
   - is_sos (INTEGER)
   - is_critical (INTEGER)
   - bia_reference_id (TEXT)
   - fallback_hash (TEXT)

2. **chat**
   - ROWID (INTEGER)
   - guid (TEXT)
   - style (INTEGER)
   - state (INTEGER)
   - account_id (TEXT)
   - properties (BLOB)
   - chat_identifier (TEXT)
   - service_name (TEXT)
   - room_name (TEXT)
   - account_login (TEXT)
   - is_archived (INTEGER)
   - last_addressed_handle (TEXT)
   - display_name (TEXT)
   - group_id (TEXT)
   - is_filtered (INTEGER)
   - successful_query (INTEGER)
   - engram_id (TEXT)
   - server_change_token (TEXT)
   - ck_sync_state (INTEGER)
   - original_group_id (TEXT)
   - last_read_message_timestamp (INTEGER)
   - cloudkit_record_id (TEXT)
   - last_addressed_sim_id (TEXT)
   - is_blackholed (INTEGER)
   - syndication_date (INTEGER)
   - syndication_type (INTEGER)
   - is_recovered (INTEGER)
   - is_deleting_incoming_messages (INTEGER)

3. **handle**
   - ROWID (INTEGER)
   - id (TEXT)
   - country (TEXT)
   - service (TEXT)
   - uncanonicalized_id (TEXT)
   - person_centric_id (TEXT)

4. **attachment**
   - ROWID (INTEGER)
   - guid (TEXT)
   - created_date (INTEGER)
   - start_date (INTEGER)
   - filename (TEXT)
   - uti (TEXT)
   - mime_type (TEXT)
   - transfer_state (INTEGER)
   - is_outgoing (INTEGER)
   - user_info (BLOB)
   - transfer_name (TEXT)
   - total_bytes (INTEGER)
   - is_sticker (INTEGER)
   - sticker_user_info (BLOB)
   - attribution_info (BLOB)
   - hide_attachment (INTEGER)
   - ck_sync_state (INTEGER)
   - ck_server_change_token_blob (BLOB)
   - ck_record_id (TEXT)
   - original_guid (TEXT)
   - is_commsafety_sensitive (INTEGER)

5. **chat_message_join**
   - chat_id (INTEGER)
   - message_id (INTEGER)
   - message_date (INTEGER)

6. **chat_handle_join**
   - chat_id (INTEGER)
   - handle_id (INTEGER)

7. **message_attachment_join**
   - message_id (INTEGER)
   - attachment_id (INTEGER)

These tables form the core structure of the iMessages database, allowing for efficient storage and retrieval of messages, chats, contacts, and attachments.
