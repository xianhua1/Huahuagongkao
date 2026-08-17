package com.ruoyi.system.domain;

/** 申论题目 */
public class ShenLunQuestion {
    private Long id;
    private Long paperId;
    private Integer qno;
    private String title;
    private Integer score;
    private Integer wordLimit;
    private String refAnswer;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getPaperId() { return paperId; }
    public void setPaperId(Long paperId) { this.paperId = paperId; }
    public Integer getQno() { return qno; }
    public void setQno(Integer qno) { this.qno = qno; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public Integer getScore() { return score; }
    public void setScore(Integer score) { this.score = score; }
    public Integer getWordLimit() { return wordLimit; }
    public void setWordLimit(Integer wordLimit) { this.wordLimit = wordLimit; }
    public String getRefAnswer() { return refAnswer; }
    public void setRefAnswer(String refAnswer) { this.refAnswer = refAnswer; }
}
