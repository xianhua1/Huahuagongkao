package com.ruoyi.system.service;

import java.util.List;
import java.util.Map;
import com.ruoyi.system.domain.ShenLunAnswer;
import com.ruoyi.system.domain.ShenLunMaterial;
import com.ruoyi.system.domain.ShenLunPaper;
import com.ruoyi.system.domain.ShenLunQuestion;

/** 申论题库服务 */
public interface IShenLunService {

    List<ShenLunPaper> selectPaperList(ShenLunPaper paper);

    Map<String, Object> getPaperDetail(Long paperId);

    List<ShenLunPaper> selectPaperPage(ShenLunPaper paper);

    int addPaper(ShenLunPaper paper);

    int updatePaper(ShenLunPaper paper);

    int deletePaper(Long paperId);

    ShenLunMaterial getMaterial(Long materialId);

    int addMaterial(ShenLunMaterial material);

    int updateMaterial(ShenLunMaterial material);

    int deleteMaterial(Long materialId);

    ShenLunQuestion getQuestion(Long questionId);

    int addQuestion(ShenLunQuestion question);

    int updateQuestion(ShenLunQuestion question);

    int deleteQuestion(Long questionId);

    /** 保存作答 */
    Long submitAnswer(Long userId, Long paperId, String content);

    /** 大模型评分（参考参考答案） */
    Map<String, Object> grade(Long userId, Long paperId, String content);

    List<Map<String, Object>> myAnswers(Long userId);

    /** 读取大模型配置 */
    Map<String, String> getLlmConfig();

    /** 保存大模型配置 */
    void saveLlmConfig(Map<String, String> cfg);
}
