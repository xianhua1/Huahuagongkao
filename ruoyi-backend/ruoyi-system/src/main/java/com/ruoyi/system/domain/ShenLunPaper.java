package com.ruoyi.system.domain;

import java.util.Date;

/** 申论试卷 */
public class ShenLunPaper {
    private Long id;
    private String paperCode;
    private String title;
    private Integer year;
    private String version;
    private Integer questionCount;
    private Date createTime;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getPaperCode() { return paperCode; }
    public void setPaperCode(String paperCode) { this.paperCode = paperCode; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public Integer getYear() { return year; }
    public void setYear(Integer year) { this.year = year; }
    public String getVersion() { return version; }
    public void setVersion(String version) { this.version = version; }
    public Integer getQuestionCount() { return questionCount; }
    public void setQuestionCount(Integer questionCount) { this.questionCount = questionCount; }
    public Date getCreateTime() { return createTime; }
    public void setCreateTime(Date createTime) { this.createTime = createTime; }
}
