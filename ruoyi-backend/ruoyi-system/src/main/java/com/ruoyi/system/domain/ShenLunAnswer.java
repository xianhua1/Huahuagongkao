package com.ruoyi.system.domain;

import java.util.Date;

/** 申论作答记录 */
public class ShenLunAnswer {
    private Long id;
    private Long userId;
    private Long paperId;
    private String content;
    private String gradeJson;
    private Integer status;
    private Date createTime;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    public Long getPaperId() { return paperId; }
    public void setPaperId(Long paperId) { this.paperId = paperId; }
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    public String getGradeJson() { return gradeJson; }
    public void setGradeJson(String gradeJson) { this.gradeJson = gradeJson; }
    public Integer getStatus() { return status; }
    public void setStatus(Integer status) { this.status = status; }
    public Date getCreateTime() { return createTime; }
    public void setCreateTime(Date createTime) { this.createTime = createTime; }
}
