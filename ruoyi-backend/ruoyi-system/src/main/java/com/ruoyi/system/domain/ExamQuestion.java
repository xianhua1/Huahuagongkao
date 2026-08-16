package com.ruoyi.system.domain;

import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 题目 exam_question
 */
public class ExamQuestion extends BaseEntity {
    private static final long serialVersionUID = 1L;

    private Long id;
    private Long paperId;
    private Long materialId;
    /** 题型（常识判断/言语理解与表达/数量关系/判断推理/资料分析） */
    private String section;
    /** 卷内原题号 */
    private Integer qno;
    /** 全卷顺序号（展示用） */
    private Integer qorder;
    /** 题干 HTML */
    private String stem;
    /** 选项 JSON：[{"label":"A","html":"..."}] */
    private String options;
    /** 正确答案 */
    private String answer;
    /** 解析 */
    private String analysis;
    /** 是否含图片 */
    private Integer hasImage;
    /** 查询辅助：只查无答案的题 */
    private String answerEmpty;
    /** 新增题目时附带的新建材料内容（非表字段） */
    private String materialContent;
    /** 新增题目时附带的新建材料标题（非表字段） */
    private String materialTitle;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getPaperId() { return paperId; }
    public void setPaperId(Long paperId) { this.paperId = paperId; }
    public Long getMaterialId() { return materialId; }
    public void setMaterialId(Long materialId) { this.materialId = materialId; }
    public String getSection() { return section; }
    public void setSection(String section) { this.section = section; }
    public Integer getQno() { return qno; }
    public void setQno(Integer qno) { this.qno = qno; }
    public Integer getQorder() { return qorder; }
    public void setQorder(Integer qorder) { this.qorder = qorder; }
    public String getStem() { return stem; }
    public void setStem(String stem) { this.stem = stem; }
    public String getOptions() { return options; }
    public void setOptions(String options) { this.options = options; }
    public String getAnswer() { return answer; }
    public void setAnswer(String answer) { this.answer = answer; }
    public String getAnalysis() { return analysis; }
    public void setAnalysis(String analysis) { this.analysis = analysis; }
    public Integer getHasImage() { return hasImage; }
    public void setHasImage(Integer hasImage) { this.hasImage = hasImage; }
    public String getAnswerEmpty() { return answerEmpty; }
    public void setAnswerEmpty(String answerEmpty) { this.answerEmpty = answerEmpty; }
    public String getMaterialContent() { return materialContent; }
    public void setMaterialContent(String materialContent) { this.materialContent = materialContent; }
    public String getMaterialTitle() { return materialTitle; }
    public void setMaterialTitle(String materialTitle) { this.materialTitle = materialTitle; }
}
