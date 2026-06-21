# Implementation Guide — Class Attendance Management System

This document is a complete implementation specification derived from the project's UML class diagram. It is written so that an AI coding agent (or a human developer) can implement the full system without needing to see the diagram image. Follow every section in order. Do not deviate from the constraints in Section 1 — they are graded requirements, not suggestions.

---

## 1. Hard Constraints (MUST / MUST NOT)

- **MUST** be implemented in exactly one of: C, C++, C#, Java, Python.
- **MUST NOT** use any built-in dynamic collection type for application data: no `List`/`ArrayList`/`array`/`vector`/`Dictionary`/`HashMap`/`Queue`/`set` from the language's standard library. The only allowed collection in the entire codebase is the custom `MyLinkedList<T>` defined in Section 4.
- **MUST NOT** use built-in sort or search functions (`sort()`, `sorted()`, `Collections.sort`, `Array.Find`, `LINQ`, `.find()`/`.indexOf()` of native arrays, etc.). All searching and sorting must be hand-written, traversing `MyLinkedList<T>` node by node.
- **MUST NOT** use built-in string-splitting utilities (`split()`, `String.Split`, etc.) to parse the data files. Write a manual character-by-character field parser.
- **MUST** be menu-driven: the program loops, showing a menu, until the user explicitly chooses to exit.
- **MUST** persist all data to plain text files, and reload it on startup.
- All in-code identifiers (classes, fields, methods) **MUST** match the names in Section 5 exactly — an AI agent or grader will cross-check the diagram against the code.

---

## 2. Architecture Overview

Five layers, top to bottom:

```
MainProgram          (presentation / menu loop)
      |
AttendanceManager     (facade / orchestration)
      |        \
SchoolClass    AttendanceReport, FileManager
      |   \
Schedule  Session
            |
      AttendanceRecord --- AttendanceStatus (enum)
            |
         Student

MyLinkedList<T> + Node<T>   (custom data structure, used by every layer above)
```

Rule of thumb for where logic belongs:
- **MainProgram**: only prints menus and reads input. Contains no business logic.
- **AttendanceManager**: the single entry point MainProgram talks to. Owns the top-level list of classes. Exposes facade methods so MainProgram never has to chain calls across multiple objects itself.
- **SchoolClass**: owns its own students, schedule entries, and sessions. Knows how to compute one student's absence rate.
- **Session**: owns the attendance records of one specific class meeting on one specific date.
- **AttendanceReport**: read-only queries across a SchoolClass's data (ranking, warnings, per-session stats). Does not mutate anything.
- **FileManager**: pure I/O, no business logic.

---

## 3. Naming & Status Values

`AttendanceStatus` enumeration has exactly 3 values:

| Enum value | Meaning (Vietnamese) |
|---|---|
| `PRESENT` | Có mặt |
| `EXCUSED_ABSENCE` | Vắng có phép |
| `UNEXCUSED_ABSENCE` | Vắng không phép |

If the host language has no native enum, or if using one would violate Section 1, represent it as string constants (e.g. `"PRESENT"`, `"EXCUSED_ABSENCE"`, `"UNEXCUSED_ABSENCE"`) defined once in a constants module — do not hardcode the strings throughout the codebase.

---

## 4. Custom Data Structure (implement this first — everything else depends on it)

### 4.1 `Node<T>`
| Field | Type |
|---|---|
| `data` | `T` |
| `next` | `Node<T>` (nullable) |

### 4.2 `MyLinkedList<T>`
Singly linked list with head/tail pointers.

| Field | Type |
|---|---|
| `head` | `Node<T>` (nullable) |
| `tail` | `Node<T>` (nullable) |
| `size` | `int` |

| Method | Behavior |
|---|---|
| `addLast(item: T)` | Append to the end. O(1) using `tail`. |
| `remove(item: T) : bool` | Linear scan; remove the **first** node whose data equals/matches `item` (define equality as appropriate per call site — usually via a predicate, see `find`). Return `true` if removed, `false` if not found. Update `head`/`tail` correctly if removing the first/last node. |
| `find(condition) : T` | Linear scan; `condition` is a predicate function `T -> bool`. Return the first matching `data`, or `null`/`None` if none match. |
| `traverse(action)` | Linear scan calling `action(data)` for every element, in order. Used for printing/iterating. |
| `size() : int` | Return `size` (already tracked, O(1) — do not recount). |

This class is generic and is the **only** collection type used anywhere else in the program — for the class list, student lists, schedule lists, session lists, attendance lists, and every "search results" / "report" list returned by other classes.

---

## 5. Domain & Service Classes

For each class below: fields first, then methods, then behavior notes. Implement in this order (top to bottom respects dependencies).

### 5.1 `Student`
| Field | Type |
|---|---|
| `studentId` | `string` |
| `fullName` | `string` |

| Method | Returns | Behavior |
|---|---|---|
| `getStudentId()` | `string` | Plain getter. |
| `getFullName()` | `string` | Plain getter. |

### 5.2 `Schedule`
| Field | Type |
|---|---|
| `dayOfWeek` | `int` (1–7, or use a small fixed encoding — document your choice in code comments) |
| `period` | `int` |
| `room` | `string` |

No methods beyond constructor; it is a plain data holder.

### 5.3 `AttendanceStatus` (enum / constants)
See Section 3.

### 5.4 `AttendanceRecord`
| Field | Type |
|---|---|
| `student` | `Student` (object reference, not just an ID) |
| `status` | `AttendanceStatus` |

| Method | Returns | Behavior |
|---|---|---|
| `getStatus()` | `AttendanceStatus` | Plain getter. |
| `setStatus(status)` | — | Plain setter; validate `status` is one of the 3 allowed values before assigning. |

### 5.5 `Session`
Represents one specific class meeting (one `SchoolClass`, one date).

| Field | Type |
|---|---|
| `date` | `Date` (or `string` in `YYYY-MM-DD` format if the language has no convenient date type) |
| `attendanceList` | `MyLinkedList<AttendanceRecord>` |

| Method | Returns | Behavior |
|---|---|---|
| `recordAttendance(studentId, status)` | — | Resolve `studentId` to a `Student` object (see implementation note below), reject if a record for that student already exists in `attendanceList` (return/raise an error — do not silently overwrite), otherwise construct a new `AttendanceRecord` and `addLast` it. |
| `findAttendance(studentId)` | `AttendanceRecord` | `attendanceList.find(r => r.student.getStudentId() == studentId)`. |
| `countPresent()` | `int` | Traverse `attendanceList`, count records where `status == PRESENT`. |

**Implementation note (important — the diagram does not show this detail):** `Session.recordAttendance(studentId, status)` needs to turn a `studentId` into a `Student` object, but `Session` does not own the student roster — `SchoolClass` does. Resolve this with one of:
- **(Recommended)** `SchoolClass.createSession(date)` injects a reference (or a lookup callback) into the new `Session` so it can resolve `studentId → Student` against the owning class's `studentList`.
- Alternatively, move student resolution one level up: `SchoolClass` resolves the `Student` first, then calls a lower-level `Session` method that accepts the resolved `Student` object directly. If you take this path, keep the **public** facade method signature `recordAttendance(studentId, status)` so the rest of the design is unaffected.

Either approach is acceptable; pick one and apply it consistently. Document the choice in a code comment at the top of `session.*`.

### 5.6 `SchoolClass`
| Field | Type |
|---|---|
| `classId` | `string` |
| `className` | `string` |
| `studentList` | `MyLinkedList<Student>` |
| `scheduleList` | `MyLinkedList<Schedule>` |
| `sessionList` | `MyLinkedList<Session>` |

| Method | Returns | Behavior |
|---|---|---|
| `addStudent(student)` | — | Reject (return `false` / raise) if `student.studentId` already exists in `studentList`. Otherwise `addLast`. |
| `getStudentList()` | `MyLinkedList<Student>` | Plain getter, returns the live list (used by the menu's "view students in class" option). |
| `addSchedule(schedule)` | — | `addLast` onto `scheduleList`. No uniqueness constraint required, but consider warning on an exact duplicate (same day/period/room). |
| `createSession(date)` | `Session` | If a session for `date` already exists in `sessionList`, return the existing one instead of creating a duplicate. Otherwise construct a new `Session(date)`, `addLast` it, return it. |
| `findSession(date)` | `Session` | `sessionList.find(s => s.date == date)`. Returns `null`/`None` if not found — **does not** create one (that is `createSession`'s job). |
| `calculateAbsenceRate(studentId)` | `float` | Traverse `sessionList`; for each session call `findAttendance(studentId)`. Count `totalSessions` = number of sessions where a record for this student exists; count `absences` = number of those records whose status is `EXCUSED_ABSENCE` or `UNEXCUSED_ABSENCE`. Return `0.0` if `totalSessions == 0` (avoid division by zero). Otherwise return `absences * 100.0 / totalSessions`. |

### 5.7 `AttendanceReport`
Stateless — takes a `SchoolClass` as a parameter on every call rather than storing one.

| Method | Returns | Behavior |
|---|---|---|
| `reportAttendanceBySession(session)` | (prints / returns a summary) | Count `present`, `excusedAbsence`, `unexcusedAbsence` by traversing `session.attendanceList`. Also report `totalEnrolled - recordedCount` as "not yet recorded" if useful. |
| `getMostAbsentStudents(schoolClass)` | `MyLinkedList<Student>` (or a richer report-item type, see note) | For every student in `schoolClass.getStudentList()`, compute absence count via `schoolClass.calculateAbsenceRate`-style traversal. Sort the resulting list **descending by absence count** using a hand-written sort (bubble sort or selection sort) operating on `MyLinkedList` nodes — swap `node.data`, not pointers. |
| `getAbsenceWarningList(schoolClass)` | `MyLinkedList<Student>` | Same computation as above, but filter to only students whose absence rate (`schoolClass.calculateAbsenceRate(studentId)`) is `> 20.0`. |

Note: returning a plain `MyLinkedList<Student>` loses the computed numbers (rate, count). In practice, define a small internal report-item struct/class (e.g. `AbsenceReportItem { student, totalSessions, absenceCount, absenceRate }`) and have these two methods return `MyLinkedList<AbsenceReportItem>` instead — adjust the diagram's return type accordingly in your code comments. This does not change the public menu behavior, only the internal data carried back.

### 5.8 `AttendanceManager`
The facade. **All** menu actions go through this class (or through `AttendanceReport`/`FileManager` only by way of this class — `MainProgram` should never reach directly into a `SchoolClass`).

| Field | Type |
|---|---|
| `classList` | `MyLinkedList<SchoolClass>` |

| Method | Returns | Behavior |
|---|---|---|
| `addClass(schoolClass)` | — | Reject if `classId` already exists. Otherwise `addLast`. |
| `getAllClasses()` | `MyLinkedList<SchoolClass>` | Plain getter, for the "view class list" menu item. |
| `findClassById(classId)` | `SchoolClass` | `classList.find(c => c.classId == classId)`. |
| `recordAttendance(classId, date, studentId, status)` | — | Facade. Steps: (1) `findClassById(classId)`, error if not found; (2) verify the student is enrolled (`schoolClass.getStudentList().find(...)`), error if not; (3) `schoolClass.findSession(date)`, and if `null`, `schoolClass.createSession(date)`; (4) `session.recordAttendance(studentId, status)`. |
| `searchByDate(classId, date)` | `Session` | (1) `findClassById`, error if not found; (2) `schoolClass.findSession(date)`. |
| `searchByStudentId(studentId)` | `MyLinkedList<AttendanceRecord>` | Traverse **all** classes → all sessions → all attendance records; collect every `AttendanceRecord` whose `student.getStudentId() == studentId` into a new `MyLinkedList`. This is intentionally O(classes × sessions × records) — acceptable at this data scale; note the complexity in the report. |
| `saveData()` | — | Calls into `FileManager` per Section 6. |
| `loadData()` | — | Calls into `FileManager` per Section 6, called once at startup before the menu loop begins. |

### 5.9 `FileManager`
| Method | Behavior |
|---|---|
| `readFile(path)` | Open and read the file as plain text, return its full contents (or expose a line-iteration method — implementer's choice, as long as no built-in line-splitting-into-array call is used to *parse fields within a line*; reading raw lines from a file is fine). |
| `writeFile(path, content)` | Overwrite the file with `content`. |

### 5.10 `MainProgram`
| Field | Type |
|---|---|
| `manager` | `AttendanceManager` |

| Method | Behavior |
|---|---|
| `showMenu()` | Print the menu text (Section 8). |
| `handleChoice(choice)` | Switch/if-chain on `choice`, calling exactly one `manager.*` method (collecting any needed input from the user first), then printing the result. |
| `run()` | `manager.loadData()` once, then loop: `showMenu()` → read input → `handleChoice()` → repeat until the user picks "exit", at which point call `manager.saveData()` before terminating. |

---

## 6. Relationships Summary

| From | To | Type | Cardinality | Meaning |
|---|---|---|---|---|
| MainProgram | AttendanceManager | association | 1 → 1 | controls |
| AttendanceManager | FileManager | association | 1 → 1 | read/write data |
| AttendanceManager | AttendanceReport | association | 1 → 1 | generates reports |
| AttendanceManager | SchoolClass | **composition** | 1 → 0..* | manages; classes do not outlive the manager |
| SchoolClass | Student | **aggregation** | 1 → 0..* | enrolls; a student could conceptually exist independently / be enrolled in multiple classes |
| SchoolClass | Schedule | **composition** | 1 → 0..* | has; schedule entries belong to exactly one class |
| SchoolClass | Session | **composition** | 1 → 0..* | has; sessions belong to exactly one class |
| Session | AttendanceRecord | **composition** | 1 → 0..* | records; attendance records belong to exactly one session |
| AttendanceRecord | Student | association | 0..* → 1 | belongs to |
| AttendanceRecord | AttendanceStatus | association | — | has |
| AttendanceReport | SchoolClass | dependency | — | queries only, does not store a reference |
| MyLinkedList\<T\> | Node\<T\> | composition | 1 → 0..* | stores |
| SchoolClass, Session, AttendanceManager | MyLinkedList\<T\> | dependency | — | use it as their internal collection type |

Composition (filled diamond) = the child has no independent lifecycle; deleting the parent should logically remove the children. Aggregation (open diamond) = the child can exist/be referenced independently.

---

## 7. Business Rules

- **Absence rate** for a student in a class: `(number of EXCUSED_ABSENCE + UNEXCUSED_ABSENCE records) / (total attendance records for that student in that class) * 100`. If the student has zero recorded sessions, the rate is `0.0` (not undefined/error).
- **At-risk warning**: any student whose absence rate is **strictly greater than 20%** appears in `getAbsenceWarningList`.
- **No duplicate attendance**: recording attendance for the same `(classId, date, studentId)` twice must be rejected, not silently overwritten. (If you want an "edit" capability, expose it as a separate, explicit menu action — do not fold it into `recordAttendance`.)
- **Referential checks before insert**: cannot add a student to a class that doesn't exist; cannot add a schedule to a class that doesn't exist; cannot record attendance for a student not enrolled in that class.

---

## 8. Persistence Format

In-memory the model is **nested** (a `SchoolClass` owns its students/schedules/sessions; a `Session` owns its records). On disk, store it **flattened/normalized** across plain text files, then rebuild the nested structure on load. Pipe-delimited (`|`) fields, one record per line, manual parsing only (no `split()`).

```
data/classes.txt      → classId|className
data/students.txt     → classId|studentId|fullName
data/schedules.txt    → classId|dayOfWeek|period|room
data/sessions.txt     → classId|date
data/attendance.txt   → classId|date|studentId|status
```

### `loadData()` algorithm
1. Read `classes.txt` line by line → construct `SchoolClass` objects → `AttendanceManager.addClass(...)`.
2. Read `students.txt` → for each line, `findClassById(classId)` then `schoolClass.addStudent(new Student(...))`.
3. Read `schedules.txt` → similarly, `schoolClass.addSchedule(new Schedule(...))`.
4. Read `sessions.txt` → for each line, `findClassById(classId)` then `schoolClass.createSession(date)` (idempotent — safe even though step 5 will also implicitly need the session to exist).
5. Read `attendance.txt` → for each line, `findClassById(classId)`, `schoolClass.findSession(date)` (must exist by now from step 4), then call the lower-level record-insertion path used internally by `Session.recordAttendance` to rebuild the `AttendanceRecord` (resolving `studentId → Student` via `schoolClass.getStudentList().find(...)`).

### `saveData()` algorithm
Traverse `classList`; for each `SchoolClass`, write one line to `classes.txt`, then traverse its `studentList` (write to `students.txt`), `scheduleList` (write to `schedules.txt`), and `sessionList` — for each `Session`, write one line to `sessions.txt`, then traverse its `attendanceList` and write one line per record to `attendance.txt`. Overwrite all 5 files completely on every save (simplest correct approach at this data scale).

---

## 9. Menu Specification

```
===== ATTENDANCE MANAGEMENT SYSTEM =====

I. CLASS MANAGEMENT
1. Add a new class                  -> manager.addClass(...)
2. View class list                  -> manager.getAllClasses(...)
3. Add a student to a class         -> schoolClass.addStudent(...)   (resolve class first via findClassById)
4. View students in a class         -> schoolClass.getStudentList(...)
5. Add/view schedule for a class    -> schoolClass.addSchedule(...) / iterate scheduleList

II. ATTENDANCE
6. Record attendance                -> manager.recordAttendance(classId, date, studentId, status)
7. Search attendance by class+date  -> manager.searchByDate(classId, date)
8. Search attendance by student ID  -> manager.searchByStudentId(studentId)
9. View a student's absence rate    -> schoolClass.calculateAbsenceRate(studentId)

III. REPORTS
10. Attendance stats for one session-> report.reportAttendanceBySession(session)
11. Most-absent students            -> report.getMostAbsentStudents(schoolClass)
12. At-risk warning list (>20%)     -> report.getAbsenceWarningList(schoolClass)

0. Save and exit                    -> manager.saveData()
==========================================
```

Every numbered item must map to exactly one (or a short, fixed sequence of) `AttendanceManager`/`AttendanceReport` call(s) as shown. `MainProgram` collects raw input (class ID, date string, student ID, status code) via prompts, then calls the manager — it must not itself loop over `MyLinkedList` internals to do business logic.

---

## 10. Validation Rules (apply at every relevant entry point)

- Reject empty/whitespace-only required fields with a clear message; do not crash.
- Reject duplicate primary identifiers (`classId`, `studentId` within a class).
- Reject foreign-key references to a non-existent class.
- Reject an attendance `status` value outside the 3 allowed values.
- All validation failures should return a boolean/error result that the caller can act on — do not use exceptions for ordinary "not found" cases unless your chosen language's idioms strongly favor it (e.g. it's fine in C#/Java to use exceptions consistently, but be consistent).

---

## 11. Acceptance Checklist

Before considering the implementation done, verify each of these end-to-end (these map directly back to the original assignment brief):

- [ ] Program is menu-driven and loops until "exit" is chosen.
- [ ] No native list/array/dict/hashmap/queue is used anywhere for application data — only `MyLinkedList<T>`.
- [ ] No built-in sort/search/split function is called anywhere in the business logic.
- [ ] Can add a class, add students to it, add a schedule to it.
- [ ] Can record attendance (Present / Excused / Unexcused) for a student on a given date.
- [ ] Can search attendance by class + date.
- [ ] Can search attendance history by student ID, across all classes.
- [ ] Absence rate is computed correctly and automatically per student.
- [ ] Students with absence rate > 20% are correctly flagged.
- [ ] Per-session attendance statistics (present/excused/unexcused counts) are correct.
- [ ] "Most absent students" list is correctly sorted descending (hand-written sort, verifiable by reading the sort code — must not call a library sort).
- [ ] All data survives a full program restart (save on exit, load on startup).
- [ ] Re-running with the same data twice produces identical output (no random ordering bugs from the custom linked list).

---

## 12. Implementation Notes

- Pick **one** language from Section 1 before starting; this guide's signatures are written language-agnostically (`method(arg) : ReturnType`) — translate directly into the chosen language's syntax.
- Keep `MyLinkedList<T>`/`Node<T>` in their own module/file, fully decoupled from the domain classes, so they can be unit-tested in isolation (try creating a small ad-hoc test: add 5 items, remove one from the middle, confirm `find`/`traverse`/`size` are still correct).
- Build bottom-up: `MyLinkedList<T>` → `Student`/`Schedule`/`AttendanceStatus` → `AttendanceRecord` → `Session` → `SchoolClass` → `AttendanceReport`/`FileManager` → `AttendanceManager` → `MainProgram`. Each layer should be manually testable before the next one is built on top of it.
