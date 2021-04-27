from library import main,book,Library,reader
import socket
from msgutils import recv_msg, send_msg
import os
from concurrent.futures import ThreadPoolExecutor
import threading

lock=threading.Lock()
library=main.library1

def start_server(ip, port):
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", port))
        s.listen(4)


        threads=[]
        while True:
            counter=1
            #conn, addr =s.accept()
            t=threading.Thread(target=work_with_client, args=(s.accept(),))
            threads.append(t)
            t.start()




def work_with_client(get_tuple):
    print('Starting thread')
    conn=get_tuple[0]

    msg ="\n\n" \
        "choose option:\n" \
              "1:show all books\n" \
              "2:show books in library\n" \
              "3:show books out of library\n" \
              "4:add book\n" \
              "5:del book\n" \
              "6:give book to reader\n" \
              "7:take book from reader\n" \
              "8:sort books base on author\n" \
              "9:sort books base on title\n" \
              "0:Close program"

    if not send_msg(conn, msg.encode()):
        return

    while True:

        choice_client=recv_msg(conn)

        if not choice_client:
            return
        choice_client=int(choice_client)


        if choice_client==1:
            answer=library.print_books("all")+msg
            send_msg(conn,answer.encode())
        elif choice_client==2:
            answer=library.print_books("lib")+msg
            send_msg(conn,answer.encode())
        elif choice_client==3:
            answer=library.print_books("any")+msg
            send_msg(conn,answer.encode())
        elif choice_client==4:
            answer="please enter book id"
            send_msg(conn, answer.encode())
            book_id=recv_msg(conn)
            answer="please enter book title"
            send_msg(conn, answer.encode())
            book_title=recv_msg(conn)
            answer = "please enter book author"
            send_msg(conn, answer.encode())
            book_author = recv_msg(conn)
            answer = "please enter book year"
            send_msg(conn, answer.encode())
            book_year = int((recv_msg(conn)))
            new_book=book.Book(book_id,book_title,book_author,book_year)
            answer+=msg


            lock.acquire()
            try:
                library.add_book(new_book)
            finally:
                lock.release()


            send_msg(conn,answer.encode())
        elif choice_client==5:
            answer="please enter book id to delete"
            send_msg(conn, answer.encode())
            book_id=recv_msg(conn)


            lock.acquire()
            try:
                library.del_book(book_id)
            finally:
                lock.release()


            answer="book deleted successfully"+msg
            send_msg(conn, answer.encode())
        elif choice_client==6:
            answer="please enter book id to take it"
            send_msg(conn,answer.encode())
            book_id=recv_msg(conn)
            answer="please enter reader id to take it"
            send_msg(conn, answer.encode())
            reader_id = recv_msg(conn)

            lock.acquire()
            try:
                if library.give_book_to_reader(book_id,reader_id)==True:
                    answer="you take the book"+msg
                    send_msg(conn, answer.encode())
                else:
                    answer = "error"+msg
                    send_msg(conn, answer.encode())
            finally:
                lock.release()
        elif choice_client==7:
            answer = "please enter book id to return it"
            send_msg(conn, answer.encode())
            book_id=recv_msg(conn)

            lock.acquire()
            try:
                if library.get_book_from_reader(book_id)==True:
                    answer="you return the book"+msg
                    send_msg(conn, answer.encode())
                else:
                    answer = "error"+msg
                    send_msg(conn, answer.encode())
            finally:
                lock.release()
        elif choice_client==8:
            answer=library.sort("author")+msg
            send_msg(conn, answer.encode())
        elif choice_client==9:
            answer=library.sort("name")+msg
            send_msg(conn, answer.encode())

        elif choice_client==0:
            print("client end connection")
            return







if __name__=="__main__":
    start_server('',33450)
    with ThreadPoolExecutor as t:
        t.map(work_with_client(), list_of_conn)
