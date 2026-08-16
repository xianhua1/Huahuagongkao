package com.ruoyi.system.mapper;

import java.util.List;
import java.util.Map;
import org.apache.ibatis.annotations.Param;
import com.ruoyi.system.domain.ExamMaterial;
import com.ruoyi.system.domain.ExamPaper;
import com.ruoyi.system.domain.ExamQuestion;
import com.ruoyi.system.domain.ExamRecord;

/**
 * 题库 Mapper
 */
public interface ExamMapper {

    List<ExamPaper> selectPaperList(ExamPaper paper);

    ExamPaper selectPaperById(Long paperId);

    List<ExamMaterial> selectMaterialsByPaperId(Long paperId);

    List<ExamMaterial> selectMaterialsByIds(@Param("ids") List<Long> ids);

    List<ExamQuestion> selectQuestionsByPaperId(Long paperId);

    ExamQuestion selectQuestionById(Long questionId);

    List<ExamQuestion> selectRandomQuestions(@Param("section") String section, @Param("count") int count);

    List<ExamQuestion> selectQuestionPage(ExamQuestion question);

    int updateQuestion(ExamQuestion question);

    int insertQuestion(ExamQuestion question);

    int selectMaxQorder(Long paperId);

    int insertMaterial(ExamMaterial material);

    int updateMaterialContent(ExamMaterial material);

    ExamMaterial selectMaterialById(Long materialId);

    int insertPaper(ExamPaper paper);

    int insertRecord(ExamRecord record);

    int updateRecord(ExamRecord record);

    ExamRecord selectRecord(@Param("userId") Long userId, @Param("questionId") Long questionId);

    List<Map<String, Object>> selectWrongList(@Param("userId") Long userId);

    Map<String, Object> selectPaperStats(@Param("userId") Long userId, @Param("paperId") Long paperId);

    List<Map<String, Object>> selectAnsweredRecords(@Param("userId") Long userId, @Param("paperId") Long paperId);

    int deleteRecord(@Param("userId") Long userId, @Param("questionId") Long questionId);

    int deleteWrongRecords(@Param("userId") Long userId);

    Map<String, Object> selectDashboardStats(@Param("userId") Long userId);

    List<Map<String, Object>> selectSectionStats(@Param("userId") Long userId);
}
