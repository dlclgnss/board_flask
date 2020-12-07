from main import *
from flask import Blueprint


blueprint =  Blueprint("board",__name__,url_prefix="/board") #블루프린트이름,모듈이름,url


#list
@blueprint.route("/list")  # app⇒blueprint #블루프린트로설정된것은 url에 board가붙어서 나옴 /board/list
def lists():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 7, type=int)

    search = request.args.get("search", -1, type=int)
    keyword = request.args.get("keyword", "", type=str) #keyword옆에 빈문자열로 해주면 None으로 표시되지 않는다.

    #최종적으로 완성된 쿼리를 만드는 변수
    query = {}
    search_list = []

    if search == 0:
        search_list.append({"title": {"$regex": keyword}})
    elif search == 1:
        search_list.append({"contents": {"$regex": keyword}})
    elif search == 2:
        search_list.append({"title": {"$regex": keyword}})
        search_list.append({"contents": {"$regex": keyword}})
    elif search == 3:
        search_list.append({"name": {"$regex": keyword}})

    if len(search_list) > 0:
        query = {"$or": search_list}

    board = mongo.db.board
    # 2page경우/ 2-1 = 1 / 1x7 =7 / 7페이지부터 출력이라는 뜻 / 주어진 숫자만큼 스킵/ limit() 인자로 주어진 숫자 만큼 보여줌
    # sort 함수를 써서 새로운글이 맨앞으로 오게한다.
    datas = board.find(query).skip((page-1) * limit).limit(limit).sort("pub_date",-1)

    #게시물의 총 갯수
    #마지막페이지 수 (전체게시물 / 페이지당 게시물 수 = 마지막페이지), 소수점 올림
    tot_count = board.find(query).count()
    last_page_num = math.ceil(tot_count / limit)

    block_size = 5
     #현재 블럭의 위치(첫 번째 블럭이라면, block_num = 0)
    block_num = int((page-1) / block_size)
    #현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
    block_start = int((block_size * block_num) + 1)
    #현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
    block_last = math.ceil(block_start + (block_size-1))

    return render_template("list.html", 
                            datas=datas, 
                            limit=limit, 
                            page=page,
                            block_start=block_start,
                            block_last=block_last,
                            last_page=last_page_num,
                            search=search,
                            keyword=keyword,
                            title = "게시판 리스트"
                            )



#상세글
@blueprint.route("/view")
@login_required
def board_view():
    idx = request.args.get("idx")
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", -1, type=int)
    keyword = request.args.get("keyword", "", type=str)

    if idx is not None:
        board = mongo.db.board
        #data = board.find_one({"_id": ObjectId(idx)})
        #(return_document=True) 업데이트한 내용을 적용할것인가 옵션
        data = board.find_one_and_update({"_id": ObjectId(idx)}, {"$inc": {"view": 1}}, return_document=True)
        # print("view_data: ",data)
        if data is not None:
            result = {
                "id": data.get("_id"),
                "name": data.get("name"),
                "title": data.get("title"),
                "contents": data.get("contents"),
                "pub_date": data.get("pub_date"),
                "view": data.get("view"),
                "writer_id":data.get("writer_id", "")
            }

            return render_template("view.html", result=result, page=page, search=search, keyword=keyword,title="상세페이지")
    return abort(404)



#게시물작성
@blueprint.route("/write", methods=["GET", "POST"])
@login_required
def board_write():
    if request.method == "POST":
        name = request.form.get("name")
        title = request.form.get("title")
        contents = request.form.get("contents")

        current_utc_time = round(datetime.utcnow().timestamp() * 1000)

        board = mongo.db.board

        post = {
            "name": name,
            "title": title,
            "contents": contents,
            "view": 0,
            "pub_date": current_utc_time,
            "writer_id": session.get("id") #unique 글수정,삭제시 본인계정인지 확인
        }
        x = board.insert_one(post)

        flash("정상적으로 작성 되었습니다.")
        return redirect(url_for("board.board_view", idx=x.inserted_id))
    else:
        return render_template("write.html",title="글 작성")




#글 수정
@blueprint.route("/edit/<idx>",methods=["GET","POST"])
def board_edit(idx):
    # 수정할 내용의 게시물 표시
    if request.method == "GET":
        #수정권한 확인
        board = mongo.db.board
        data = board.find_one({"_id": ObjectId(idx)})
        
        if data is None:
            flash("해당 게시물이 존재하지 않습니다.")
            return redirect(url_for("board.lists"))
        else:
            if session["id"] == data.get("writer_id"):
                return render_template("edit.html", data=data, title="글 수정")
            else:
                flash("글수정 권한이 없습니다.")
                return redirect(url_for("board.lists"))

    # 수정한 내용 post로 전송
    else: 
        title = request.form.get('title')
        contents = request.form.get('contents')

        #수정권한 확인
        board = mongo.db.board
        data = board.find_one({"_id": ObjectId(idx)})

        if session["id"] == data.get("writer_id"):
            board.update_one({"_id": ObjectId(idx)},{
             "$set": {
                 "title": title,
                 "contents": contents
             }   
            })
            
            flash("수정이 완료되었습니다.")
            return redirect(url_for('board.board_view',idx=idx))
        else:
            flash("글수정 권한이 없습니다.")
            return redirect(url_for("board.lists"))



# 글 삭제
@blueprint.route("/delete/<idx>")
def board_delete(idx):
    board = mongo.db.board
    # 삭제권한 확인
    data = board.find_one({"_id":ObjectId(idx)})

    if data.get("writer_id") == session["id"] :
        board.delete_one({"_id":ObjectId(idx)})
        flash("삭제 되었습니다.")
    else:
        flash("삭제 권한이 없습니다.")
    return redirect(url_for("board.lists"))