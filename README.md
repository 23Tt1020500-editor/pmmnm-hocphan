# Phần 4: Báo cáo kết quả

## 1. Danh sách route (`flask --app sodiem routes`)

```text
Endpoint                 Methods  Rule
-----------------------  -------  ----------------------------------------------
api_course_score_post    POST     /api/students/<mssv>/scores/<course>
api_manage_course_score  DELETE   /api/students/<mssv>/scores/<course>
api_manage_course_score  GET      /api/students/<mssv>/scores/<course>
api_manage_course_score  PUT      /api/students/<mssv>/scores/<course>
api_student_detail       GET      /api/students/<mssv>
api_students             GET      /api/students
export_csv               GET      /students/<mssv>/export
home                     GET      /
search                   GET      /search
short_student_link       GET      /sv/<mssv>
static                   GET      /static/<path:filename>
student_detail           GET      /students/<mssv>
student_list             GET      /students