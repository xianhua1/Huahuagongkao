package com.ruoyi.system.mapper;

import java.util.List;
import java.util.Map;
import org.apache.ibatis.annotations.Param;
import com.ruoyi.system.domain.ShenLunAnswer;
import com.ruoyi.system.domain.ShenLunMaterial;
import com.ruoyi.system.domain.ShenLunPaper;
import com.ruoyi.system.domain.ShenLunQuestion;

/** 申论题库 Mapper */
public interface ShenLunMapper {

    List<ShenLunPaper> selectPaperList(ShenLunPaper paper);

    ShenLunPaper selectPaperById(Long paperId);

    List<ShenLunMaterial> selectMaterialsByPaperId(Long paperId);

    List<ShenLunQuestion> selectQuestionsByPaperId(Long paperId);

    ShenLunQuestion selectQuestionById(Long questionId);

    ShenLunMaterial selectMaterialById(Long materialId);

    int insertPaper(ShenLunPaper paper);

    int updatePaper(ShenLunPaper paper);

    int deletePaper(Long paperId);

    int insertMaterial(ShenLunMaterial material);

    int updateMaterial(ShenLunMaterial material);

    int deleteMaterial(Long materialId);

    int deleteMaterialsByPaperId(Long paperId);

    int insertQuestion(ShenLunQuestion question);

    int updateQuestion(ShenLunQuestion question);

    int deleteQuestion(Long questionId);

    int deleteQuestionsByPaperId(Long paperId);

    int insertAnswer(ShenLunAnswer answer);

    List<Map<String, Object>> selectAnswersByUser(@Param("userId") Long userId);

    List<ShenLunPaper> selectPaperPage(ShenLunPaper paper);
}
