package com.ruoyi.system.service.impl;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.system.domain.ExamMaterial;
import com.ruoyi.system.domain.ExamPaper;
import com.ruoyi.system.domain.ExamQuestion;
import com.ruoyi.system.domain.ExamRecord;
import com.ruoyi.system.mapper.ExamMapper;
import com.ruoyi.system.service.IExamService;

@Service
public class ExamServiceImpl implements IExamService {

    @Autowired
    private ExamMapper examMapper;

    @Override
    public List<ExamPaper> selectPaperList(ExamPaper paper) {
        return examMapper.selectPaperList(paper);
    }

    @Override
    public Map<String, Object> getPaperDetail(Long paperId) {
        Map<String, Object> result = new HashMap<>();
        result.put("paper", examMapper.selectPaperById(paperId));
        result.put("materials", examMapper.selectMaterialsByPaperId(paperId));
        result.put("questions", examMapper.selectQuestionsByPaperId(paperId));
        return result;
    }

    @Override
    public ExamQuestion getQuestion(Long questionId) {
        return examMapper.selectQuestionById(questionId);
    }

    @Override
    public ExamMaterial getMaterial(Long materialId) {
        return examMapper.selectMaterialById(materialId);
    }

    @Override
    public List<ExamQuestion> selectQuestionPage(ExamQuestion question) {
        return examMapper.selectQuestionPage(question);
    }

    @Override
    public int updateQuestion(ExamQuestion question) {
        // 材料更新/新建
        if (StringUtils.isNotBlank(question.getMaterialContent())) {
            if (question.getMaterialId() != null) {
                ExamMaterial mat = new ExamMaterial();
                mat.setId(question.getMaterialId());
                mat.setContent(question.getMaterialContent());
                mat.setTitle(question.getMaterialTitle());
                examMapper.updateMaterialContent(mat);
            } else {
                ExamMaterial mat = new ExamMaterial();
                mat.setPaperId(question.getPaperId());
                mat.setSection(question.getSection());
                mat.setTitle(question.getMaterialTitle());
                mat.setContent(question.getMaterialContent());
                examMapper.insertMaterial(mat);
                question.setMaterialId(mat.getId());
            }
        }
        String stem = question.getStem() == null ? "" : question.getStem();
        String options = question.getOptions() == null ? "[]" : question.getOptions();
        question.setStem(stem);
        question.setOptions(options);
        question.setHasImage(stem.contains("<img") || options.contains("<img") ? 1 : 0);
        return examMapper.updateQuestion(question);
    }

    @Override
    public int addQuestion(ExamQuestion question) {
        if (question.getQorder() == null || question.getQorder() <= 0) {
            question.setQorder(examMapper.selectMaxQorder(question.getPaperId()) + 1);
        }
        if (question.getQno() == null) {
            question.setQno(question.getQorder());
        }
        String stem = question.getStem() == null ? "" : question.getStem();
        String options = question.getOptions() == null ? "[]" : question.getOptions();
        question.setStem(stem);
        question.setOptions(options);
        // 附带的新建材料
        if (StringUtils.isNotBlank(question.getMaterialContent())) {
            ExamMaterial mat = new ExamMaterial();
            mat.setPaperId(question.getPaperId());
            mat.setSection(question.getSection());
            mat.setTitle(question.getMaterialTitle());
            mat.setContent(question.getMaterialContent());
            examMapper.insertMaterial(mat);
            question.setMaterialId(mat.getId());
        }
        question.setHasImage(stem.contains("<img") || options.contains("<img")
                || (question.getMaterialContent() != null && question.getMaterialContent().contains("<img")) ? 1 : 0);
        return examMapper.insertQuestion(question);
    }

    @Override
    public Map<String, Object> randomQuestions(String section, int count) {
        List<ExamQuestion> questions = examMapper.selectRandomQuestions(section, count);
        List<Long> matIds = new ArrayList<>();
        for (ExamQuestion q : questions) {
            if (q.getMaterialId() != null && !matIds.contains(q.getMaterialId())) {
                matIds.add(q.getMaterialId());
            }
        }
        List<ExamMaterial> materials = matIds.isEmpty() ? new ArrayList<>()
                : examMapper.selectMaterialsByIds(matIds);
        Map<String, Object> result = new HashMap<>();
        result.put("questions", questions);
        result.put("materials", materials);
        return result;
    }

    @Override
    public Map<String, Object> saveRecord(Long userId, Long questionId, String userAnswer) {
        ExamQuestion q = examMapper.selectQuestionById(questionId);
        Map<String, Object> result = new HashMap<>();
        if (q == null) {
            result.put("success", false);
            result.put("msg", "题目不存在");
            return result;
        }
        String right = q.getAnswer() == null ? "" : q.getAnswer().trim().toUpperCase();
        String mine = userAnswer == null ? "" : userAnswer.trim().toUpperCase();
        boolean correct = StringUtils.isNotEmpty(right) && right.equals(mine);
        ExamRecord record = new ExamRecord();
        record.setUserId(userId);
        record.setQuestionId(questionId);
        record.setUserAnswer(mine);
        record.setIsCorrect(correct ? 1 : 0);
        examMapper.insertRecord(record);
        result.put("success", true);
        result.put("correct", correct);
        result.put("rightAnswer", right);
        result.put("analysis", q.getAnalysis());
        result.put("hasAnswer", StringUtils.isNotEmpty(right));
        return result;
    }

    @Override
    public Map<String, Object> paperStats(Long userId, Long paperId) {
        return examMapper.selectPaperStats(userId, paperId);
    }

    @Override
    public List<Map<String, Object>> wrongList(Long userId) {
        return examMapper.selectWrongList(userId);
    }

    @Override
    public List<Map<String, Object>> answeredRecords(Long userId, Long paperId) {
        return examMapper.selectAnsweredRecords(userId, paperId);
    }

    @Override
    public int removeRecord(Long userId, Long questionId) {
        return examMapper.deleteRecord(userId, questionId);
    }

    @Override
    public int clearWrong(Long userId) {
        return examMapper.deleteWrongRecords(userId);
    }

    @Override
    public int addPaper(ExamPaper paper) {
        if (StringUtils.isEmpty(paper.getPaperCode())) {
            paper.setPaperCode("custom-" + System.currentTimeMillis());
        }
        if (StringUtils.isEmpty(paper.getSubject())) {
            paper.setSubject("行测");
        }
        if (paper.getYear() == null) {
            paper.setYear(0);
        }
        if (StringUtils.isEmpty(paper.getVersion())) {
            paper.setVersion("自定义");
        }
        paper.setQuestionCount(0);
        return examMapper.insertPaper(paper);
    }

    @Override
    public Map<String, Object> dashboardStats(Long userId) {
        return examMapper.selectDashboardStats(userId);
    }

    @Override
    public List<Map<String, Object>> sectionStats(Long userId) {
        return examMapper.selectSectionStats(userId);
    }
}
