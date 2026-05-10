"""
This module handles reminder persistence using MySQL.
"""

from typing import List, Optional

import mysql.connector
from mysql.connector import errorcode
from pydantic import BaseModel

from app.utils.exceptions import ForbiddenException, NotFoundException


class ReminderItem(BaseModel):
  id: int
  list_id: int
  description: str
  completed: bool


class ReminderList(BaseModel):
  id: int
  owner: str
  name: str


class SelectedList(BaseModel):
  id: int
  owner: str
  name: str
  items: List[ReminderItem]


class MySQLStorage:
  def __init__(self, owner: str, db_config: dict):
    self.owner = owner
    self.db_config = db_config
    self.db_name = db_config["database"]

    temp_config = self.db_config.copy()
    temp_config.pop("database", None)
    self.conn = mysql.connector.connect(**temp_config)
    self.cursor = self.conn.cursor(dictionary=True)
    self._create_database()
    self.conn.database = self.db_name
    self._create_tables()

  def _create_database(self):
    try:
      self.cursor.execute(
        f"CREATE DATABASE {self.db_name} DEFAULT CHARACTER SET 'utf8'"
      )
    except mysql.connector.Error as err:
      if err.errno != errorcode.ER_DB_CREATE_EXISTS:
        raise

  def _create_tables(self):
    tables = {
      "reminder_lists": (
        "CREATE TABLE `reminder_lists` ("
        "  `id` int(11) NOT NULL AUTO_INCREMENT,"
        "  `owner` varchar(255) NOT NULL,"
        "  `name` varchar(255) NOT NULL,"
        "  PRIMARY KEY (`id`)"
        ") ENGINE=InnoDB"
      ),
      "reminder_items": (
        "CREATE TABLE `reminder_items` ("
        "  `id` int(11) NOT NULL AUTO_INCREMENT,"
        "  `list_id` int(11) NOT NULL,"
        "  `description` text NOT NULL,"
        "  `completed` boolean NOT NULL DEFAULT 0,"
        "  PRIMARY KEY (`id`),"
        "  FOREIGN KEY (`list_id`) REFERENCES `reminder_lists` (`id`) ON DELETE CASCADE"
        ") ENGINE=InnoDB"
      ),
      "selected_lists": (
        "CREATE TABLE `selected_lists` ("
        "  `owner` varchar(255) NOT NULL,"
        "  `list_id` int(11),"
        "  PRIMARY KEY (`owner`),"
        "  FOREIGN KEY (`list_id`) REFERENCES `reminder_lists` (`id`) ON DELETE SET NULL"
        ") ENGINE=InnoDB"
      ),
    }

    for table_sql in tables.values():
      try:
        self.cursor.execute(table_sql)
      except mysql.connector.Error as err:
        if err.errno != errorcode.ER_TABLE_EXISTS_ERROR:
          raise

  def _get_raw_list(self, list_id: int) -> dict:
    self.cursor.execute("SELECT * FROM reminder_lists WHERE id = %s", (list_id,))
    reminder_list = self.cursor.fetchone()
    if not reminder_list:
      raise NotFoundException()
    if reminder_list["owner"] != self.owner:
      raise ForbiddenException()
    return reminder_list

  def _get_raw_item(self, item_id: int) -> dict:
    self.cursor.execute("SELECT * FROM reminder_items WHERE id = %s", (item_id,))
    item = self.cursor.fetchone()
    if not item:
      raise NotFoundException()
    self._verify_list_exists(item["list_id"])
    return item

  def _verify_list_exists(self, list_id: int) -> None:
    self._get_raw_list(list_id)

  def _verify_item_exists(self, item_id: int) -> None:
    self._get_raw_item(item_id)

  def create_list(self, name: str) -> int:
    self.cursor.execute(
      "INSERT INTO reminder_lists (name, owner) VALUES (%s, %s)",
      (name, self.owner),
    )
    self.conn.commit()
    return self.cursor.lastrowid

  def delete_list(self, list_id: int) -> None:
    self._verify_list_exists(list_id)
    self.cursor.execute("DELETE FROM reminder_lists WHERE id = %s", (list_id,))
    self.conn.commit()

  def delete_lists(self) -> None:
    for reminder_list in self.get_lists():
      self.delete_list(reminder_list.id)

  def get_list(self, list_id: int) -> ReminderList:
    return ReminderList(**self._get_raw_list(list_id))

  def get_lists(self) -> List[ReminderList]:
    self.cursor.execute("SELECT * FROM reminder_lists WHERE owner = %s", (self.owner,))
    return [ReminderList(**row) for row in self.cursor.fetchall()]

  def update_list_name(self, list_id: int, new_name: str) -> None:
    self._verify_list_exists(list_id)
    self.cursor.execute(
      "UPDATE reminder_lists SET name = %s WHERE id = %s",
      (new_name, list_id),
    )
    self.conn.commit()

  def add_item(self, list_id: int, description: str) -> int:
    self._verify_list_exists(list_id)
    self.cursor.execute(
      "INSERT INTO reminder_items (list_id, description, completed) VALUES (%s, %s, %s)",
      (list_id, description, False),
    )
    self.conn.commit()
    return self.cursor.lastrowid

  def delete_item(self, item_id: int) -> None:
    self._verify_item_exists(item_id)
    self.cursor.execute("DELETE FROM reminder_items WHERE id = %s", (item_id,))
    self.conn.commit()

  def get_item(self, item_id: int) -> ReminderItem:
    return ReminderItem(**self._get_raw_item(item_id))

  def get_items(self, list_id: int) -> List[ReminderItem]:
    self._verify_list_exists(list_id)
    self.cursor.execute("SELECT * FROM reminder_items WHERE list_id = %s", (list_id,))
    return [ReminderItem(**row) for row in self.cursor.fetchall()]

  def strike_item(self, item_id: int) -> None:
    item = self._get_raw_item(item_id)
    self.cursor.execute(
      "UPDATE reminder_items SET completed = %s WHERE id = %s",
      (not item["completed"], item_id),
    )
    self.conn.commit()

  def update_item_description(self, item_id: int, new_description: str) -> None:
    self._verify_item_exists(item_id)
    self.cursor.execute(
      "UPDATE reminder_items SET description = %s WHERE id = %s",
      (new_description, item_id),
    )
    self.conn.commit()

  def get_selected_list_id(self) -> Optional[int]:
    self.cursor.execute("SELECT list_id FROM selected_lists WHERE owner = %s", (self.owner,))
    selected_list = self.cursor.fetchone()
    if not selected_list:
      return None
    return selected_list["list_id"]

  def get_selected_list(self) -> Optional[SelectedList]:
    list_id = self.get_selected_list_id()
    if list_id is None:
      return None

    try:
      reminder_list = self.get_list(list_id)
      reminder_items = self.get_items(list_id)
    except NotFoundException:
      self.set_selected_list(None)
      return None

    return SelectedList(
      id=reminder_list.id,
      owner=reminder_list.owner,
      name=reminder_list.name,
      items=reminder_items,
    )

  def set_selected_list(self, list_id: Optional[int]) -> None:
    self.cursor.execute(
      "INSERT INTO selected_lists (owner, list_id) VALUES (%s, %s) "
      "ON DUPLICATE KEY UPDATE list_id = %s",
      (self.owner, list_id, list_id),
    )
    self.conn.commit()

  def reset_selected_after_delete(self, deleted_id: int) -> None:
    selected_list_id = self.get_selected_list_id()
    if selected_list_id == deleted_id:
      lists = self.get_lists()
      self.set_selected_list(lists[0].id if lists else None)
