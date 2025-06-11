from django.db import models
from django.db import models
from Account.models import *

class CandidateTestMaster(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255,null=True)
    mobile = models.CharField(max_length=255,null=True)
    email = models.CharField(max_length=255,null=True)
    post = models.IntegerField(null=True)
    marks_received =  models.IntegerField(null=True)
    out_of = models.IntegerField(null=True)
    created_at = models.DateTimeField(null=True)
    created_by = models.IntegerField(null=True)
    updated_at = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    time_taken = models.CharField(max_length=255,null=True)
    percentage = models.CharField(max_length=255,null=True)
    status = models.IntegerField(null=True)
    test_start_time = models.DateTimeField(null=True)
    test_end_time = models.DateTimeField(null=True)
    performance_level = models.CharField(max_length=255,null=True)
    it_marks_received =  models.IntegerField(null=True)
    it_out_of = models.IntegerField(null=True)        
    it_percentage = models.CharField(max_length=255,null=True)
    it_performance_level = models.CharField(max_length=255,null=True)
    candidate_id = models.TextField(null=True)
    form_data_id = models.IntegerField(null=True)            

                            
    class Meta:
        db_table = 'candidate_test_master'
        
class PostMaster(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.CharField(max_length=255,null=True)
    created_at = models.DateTimeField(null=True)
    created_by = models.IntegerField(null=True)
    updated_at = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)    
    class Meta:
        db_table = 'post_master'
        
class QuestionAnswerMaster(models.Model):
    question_id = models.AutoField(primary_key=True)
    topic_id = models.IntegerField(null=True)
    question = models.CharField(max_length=255,null=True)
    choice1 = models.CharField(max_length=255,null=True)
    choice2 = models.CharField(max_length=255,null=True)
    choice3 = models.CharField(max_length=255,null=True)
    choice4 = models.CharField(max_length=255,null=True)
    correct_answer = models.CharField(max_length=255,null=True)
    created_at = models.DateTimeField(null=True)
    created_by = models.IntegerField(null=True)
    updated_at = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    status = models.IntegerField(null=True)
    class Meta:
        db_table = 'question_answer_master'
        
class CandidateAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    candidate_id = models.TextField(null=True)
    post = models.IntegerField(null=True)
    question_id = models.IntegerField(null=True)
    candidates_answer = models.CharField(max_length=255,null=True)
    is_right = models.CharField(max_length=255,null=True)
    created_at = models.DateTimeField(null=True)
    created_by = models.IntegerField(null=True)
    updated_at = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    class Meta:
        db_table = 'candidates_answer'
        
class TopicMaster(models.Model):
    id = models.AutoField(primary_key=True)
    topic = models.CharField(max_length=255,null=True)
    created_at = models.DateTimeField(null=True)
    created_by = models.IntegerField(null=True)
    updated_at = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)    
    class Meta:
        db_table = 'topic_master'
        
class PostTopicMapping(models.Model):
    id = models.AutoField(primary_key=True)
    post_id = models.IntegerField(null=True)
    topic_id = models.IntegerField(null=True) 
    no_of_questions = models.IntegerField(null=True)
    created_at = models.DateTimeField(null=True)
    created_by = models.IntegerField(null=True)
    updated_at = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)       
    class Meta:
        db_table = 'post_topic_mapping'
        
class PerformanceMaster(models.Model):
    id = models.AutoField(primary_key=True)
    performance_level = models.CharField(max_length=255,null=True)
    percentage_range = models.CharField(max_length=255,null=True)
    percentage_from = models.IntegerField(null=True) 
    percentage_upto = models.IntegerField(null=True)       
    created_at = models.DateTimeField(null=True)
    created_by = models.IntegerField(null=True)
    updated_at = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)    
    class Meta:
        db_table = 'performance_master'                 
                                        
class TemporaryQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=True)    
    candidate_id = models.TextField(null=True) 
    question_ids =  models.TextField(null=True)
    status = models.IntegerField(null=True)
    created_at = models.DateTimeField(null=True)
    created_by = models.IntegerField(null=True)
    class Meta:
        db_table = 'temporary_questions'         