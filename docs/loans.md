# Loans

## User-visible flow
1. User requests a loan from the webpage over a book (profile of a book). Optionally, he can request a interest window time.
2. If all books are under a lock, then the system would trigger an alert, requesting confirmation for the user to join the queue.
3. If not, then user receive a message of confirmation that its request has been put on the book's queue.
4. If the interest window time is due, the system would alert the user, and expire its request.
5. When the request has been attended, and a physical copy has been put to the "user book-shelf", the system would inform the event to the user. The user only has 7 days to pick up the book
6. If the user picks up the book between the 7 days, the event is registered and the loan officially starts, labeling the book as loaned.
7. If not, the system marks the book as available, terminating the event.
8. When the user returns the book between the specified range of time, the system marks the physical book as available again.
9. If not, the system alerts the user about the event, and flag them on the system.

## System-visible flow
1. System receives the loan request.
    - If the total available physical copies of the book is 0, alerts the user about the event. Is decision of the user to place the request on the queue, or not
    - If not, decreases the counter, and puts the request on the book queue.
2. As the loan request is placed on the queue, a decrement of the available books in the inventory happens (a soft lock). If the available books is zero, then no decrement happens, and the request is put on a "waiting" queue.
3. The librarian only sees the requests which are not in the waiting queue: 
    - He selects one physical copy, and assigns it to the user request. When that happens, the physical copy is hard-locked, and the system alerts the user about their book being ready to pick up.
    - If something happens: No book is available, the only book is damaged, etc, then the librarian can cancel the request through the system, marking it as "incomplete" and notifying the user about the event. The soft lock dissapears and the global counter is updated in one.
4. With the hard-lock, the physical copy holds the state on "ready for pick up".
5. When the user picks up the book, the system updates the state of the copy as loaned, and the loan starts.
6. When the user returns the book, the system marks the book as returned: destroys the hard lock, which makes it available again.c