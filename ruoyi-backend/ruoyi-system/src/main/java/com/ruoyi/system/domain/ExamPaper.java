package com.ruoyi.system.domain;

import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 试卷 exam_paper
 */
public class ExamPaper extends BaseEntity {
    private static final long serialVersionUID = 1L;

    private Long id;
    /** 卷代码，如 2020-dsj */
    private String paperCode;
    /** 试卷标题 */
    private String title;
    /** 年份 */
    private Integer year;
    /** 版本（副省级/地市级/A卷...） */
    private String version;
    /** 科目 */
    private String subject;
    /** 题目数量 */
    private Integer questionCount;

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
    public String getSubject() { return subject; }
    public void setSubject(String subject) { this.subject = subject; }
    public Integer getQuestionCount() { return questionCount; }
    public void setQuestionCount(Integer questionCount) { this.questionCount = questionCount; }
}
