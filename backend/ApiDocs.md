# Quiz Api 

## Categories
`GET '/api/categories'`

Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
Request Arguments: None
Returns: An object with a single key, categories, that contains an object of id: category_string key: value pairs.
```
CategoryList {
  "1": "Science",
  "2": "Art",
  "3": "Geography",
  "4": "History",
  "5": "Entertainment",
  "6": "Sports"
}
```

#### Qustion Model 
```
    Question {
        id: Integer;
        question: String;
        answer: String;
        category: String;
        difficulty: Integer;
    }
```

### Questions




`GET '/api/questions'`

Fetches a list of paginated questions default pagesize is 10,

Request: Arguments: page example: `'/api/questions?page=1'`

Response: 
```
    {
        success: true,
        status_code: 200,
        meta: {
            first_page: int,   
            current_page: int,
            items_per_page: int,
            last_page: int,
            total_questions: int
        },
        total_questions: int,
        questions: Questions[]
        categories: {
            "1": "Science",
            "2": "Art",
            "3": "Geography",
            "4": "History",
            "5": "Entertainment",
            "6": "Sports"
        },
        currentCategory: undefined | int
    }

```

`Post '/api/questions'`

This route accepts data in the form of a `Question` will return a 422 if not created and 201 if created


`Delete '/api/questions/<id>'`

Takes an id as a parameter and returns a 200 if item is deleted,
if an item is not deleted it returns a 422, if an item is not found it is a 404

`GET '/api/categories/<int:category_id>/questions'`

this takes a category id and returns all the questions for this category,

```
    {
        "status_code": 200,
        "meta": meta, // same as questions
        'total_questions': int,
        'current_category': string,
        "questions": Question[]
    }
```

### Quizes
Quizes are dumb this app was poorly constructucted. This is not restfull as it relies on the state of the frontend. 

`Post '/api/quizzes'`

body: accepts two attributes `quiz_category` and `previous_questions`
```
quiz_category = {
    type: "All"|"Art"|"Geography"|"History"|"Entertainment"|"Sports"
    id: number
}
// array of quesiont ids
previous_questions = int[]

```
This endpoint returns a radonm quesion given the category and the previous questions asked. 

if all questions in a category a have been asked it returns an undefined question

response: 
```
{
    "question": unefined | Question
}
```
