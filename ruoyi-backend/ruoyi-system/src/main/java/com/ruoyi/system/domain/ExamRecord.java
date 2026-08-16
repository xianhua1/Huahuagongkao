package com.ruoyi.system.domain;

import java.util.Date;

/**
 * 答题记录 exam_record
 */
public class ExamRecord {
    private Long id;
    private Long userId;
    private Long questionId;
    private String userAnswer;
    private Integer isCorrect;
    private Date answeredTime;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    public Long getQuestionId() { return questionId; }
    public void setQuestionId(Long questionId) { this.questionId = questionId; }
    public String getUserAnswer() { return userAnswer; }
    public void setUserAnswer(String userAnswer) { this.userAnswer = userAnswer; }
    public Integer getIsCorrect() { return isCorrect; }
    public void setIsCorrect(Integer isCorrect) { this.isCorrect = isCorrect; }
    public Date getAnsweredTime() { return answeredTime; }
    public void setAnsweredTime(Date answeredTime) { this.answeredTime = answeredTime; }
}
