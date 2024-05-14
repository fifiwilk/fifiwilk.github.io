from fastapi import FastAPI, HTTPException
import sqlite3
import json
from typing import Annotated
from typing import List

app = FastAPI()

@app.get('/tags')
async def list_tags():
    """
    Lists all tags in database and number of images associated
    with each tag.

    **Returns:**
    * dict(str, int): dictionary containg tag names and count of images
    """

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    tag_counts_query = """
        SELECT tag, COALESCE(COUNT(images_image_tags.image_id), 0) AS count
        FROM images_imagetag
        LEFT JOIN images_image_tags 
            ON images_imagetag.id = images_image_tags.imagetag_id
        GROUP BY tag
    """

    cursor.execute(tag_counts_query)
    tag_counts = cursor.fetchall()

    cursor.close()
    conn.close()

    tag_counts_dict = {tag: count for tag, count in tag_counts}
    return tag_counts_dict


@app.get('/images')
async def list_images():
    """
    Lists all images in the database with all tags associated with them.

    **Returns:**
    * dict(str, List[str]): dictionary containing image name and list of tags
    associated with that image
    """
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
   
    cursor.execute("SELECT images_image.id, images_image.image_title FROM images_image")
    images = cursor.fetchall()

    image_tags_dict = {}
    for image_id, image_title in images:
        image_tags_dict[image_title] = []
        tags_query = f"""
            SELECT images_imagetag.tag
            FROM images_imagetag
            RIGHT JOIN images_image_tags ON images_imagetag.id = images_image_tags.imagetag_id
            WHERE images_image_tags.image_id = {image_id}
        """
        cursor.execute(tags_query)
        tags = [item[0] for item in cursor.fetchall()]
        for tag in tags:
            image_tags_dict[image_title].append(tag)


    cursor.close()
    conn.close()

    return image_tags_dict


@app.get('/images/{tag}')
async def list_images_with_tag(tag: str):
    """
    Lists all images associated with the given tag.

    **Arguments:**
    * tag(str): name of the tag that images will be filtered by

    **Returns:**
    * List[str]: list of all image names associated with **tag**
    """

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    query = f"""
        SELECT images_image.image_title
        FROM images_image
        JOIN images_image_tags ON images_image.id = images_image_tags.image_id
        JOIN images_imagetag ON images_image_tags.imagetag_id = images_imagetag.id
        WHERE images_imagetag.tag = "{tag}"
    """

    cursor.execute(query)
    image_list = [item[0] for item in cursor.fetchall()]

    cursor.close()
    conn.close()

    return json.dumps(image_list)


@app.post('/images/del')
async def delete_images(image_ids: List[int]):
    """
    Deletes images from database based on provided ids.

    **Arguments:**
    * **image_ids(List[int]):** list of ids of images to be deleted

    **Returns:**
    * **\{'message': 'Images deleted succesfully'\}** in case of success

    In case of failure of deleting at least one image raises **HTTPException**
    and rollbacks all the changes made to database, so the state of database
    does not change in case of failure.
    """
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    try:
        for image_id in image_ids:
            # Delete all relations of the image
            cursor.execute(f"DELETE FROM images_image_editors WHERE image_id = {image_id}")
            conn.commit()
            cursor.execute(f"DELETE FROM images_image_tags WHERE image_id = {image_id}")
            conn.commit()

            # Delete image
            cursor.execute(f"DELETE FROM images_image WHERE id = {image_id}")
            conn.commit()

        cursor.close()
        conn.close()
        return {'message': 'Images deleted successfully'}
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()

        raise HTTPException(status_code=500, detail=str(e))


