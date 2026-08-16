package com.ruoyi.system.service;

import java.util.List;
import java.util.Map;
import com.ruoyi.system.domain.ExamMaterial;
import com.ruoyi.system.domain.ExamPaper;
import com.ruoyi.system.domain.ExamQuestion;

/**
 * 题库服务
 */
public interface IExamService {

    List<ExamPaper> selectPaperList(ExamPaper paper);

    Map<String, Object> getPaperDetail(Long paperId);

    ExamQuestion getQuestion(Long questionId);

    ExamMaterial getMaterial(Long materialId);

    List<ExamQuestion> selectQuestionPage(ExamQuestion question);

    int updateQuestion(ExamQuestion question);

    int addQuestion(ExamQuestion question);

    int addPaper(ExamPaper paper);

    /** 随机刷题：返回 {questions, materials} */
    Map<String, Object> randomQuestions(String section, int count);

    /** 提交答案，返回 {correct, rightAnswer, analysis} */
    Map<String, Object> saveRecord(Long userId, Long questionId, String userAnswer);

    Map<String, Object> paperStats(Long userId, Long paperId);

    List<Map<String, Object>> wrongList(Long userId);

    List<Map<String, Object>> answeredRecords(Long userId, Long paperId);

    int removeRecord(Long userId, Long questionId);

    int clearWrong(Long userId);

    Map<String, Object> dashboardStats(Long userId);

    List<Map<String, Object>> sectionStats(Long userId);
}
