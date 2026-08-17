package com.ruoyi.system.domain;

/** 申论材料 */
public class ShenLunMaterial {
    private Long id;
    private Long paperId;
    private Integer mNo;
    private String title;
    private String content;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getPaperId() { return paperId; }
    public void setPaperId(Long paperId) { this.paperId = paperId; }
    public Integer getMNo() { return mNo; }
    public void setMNo(Integer mNo) { this.mNo = mNo; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
}
