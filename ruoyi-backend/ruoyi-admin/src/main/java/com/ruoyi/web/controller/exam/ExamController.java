package com.ruoyi.web.controller.exam;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.page.TableDataInfo;
import com.ruoyi.common.utils.SecurityUtils;
import com.ruoyi.system.domain.ExamPaper;
import com.ruoyi.system.domain.ExamQuestion;
import com.ruoyi.system.service.IExamService;

/**
 * 国考刷题
 */
@RestController
@RequestMapping("/exam")
public class ExamController extends BaseController {

    @Autowired
    private IExamService examService;

    /** 首页统计 */
    @GetMapping("/dashboard")
    public AjaxResult dashboard() {
        return AjaxResult.success(examService.dashboardStats(SecurityUtils.getUserId()));
    }

    /** 试卷列表（刷题用） */
    @GetMapping("/paper/list")
    public AjaxResult listPapers(ExamPaper paper) {
        return AjaxResult.success(examService.selectPaperList(paper));
    }

    /** 试卷详情（含材料与全部题目） */
    @GetMapping("/paper/{paperId}")
    public AjaxResult paperDetail(@PathVariable Long paperId) {
        return AjaxResult.success(examService.getPaperDetail(paperId));
    }

    /** 试卷管理分页 */
    @GetMapping("/paper/page")
    public TableDataInfo paperPage(ExamPaper paper) {
        startPage();
        List<ExamPaper> list = examService.selectPaperList(paper);
        return getDataTable(list);
    }

    /** 题目管理分页 */
    @GetMapping("/question/page")
    public TableDataInfo questionPage(ExamQuestion question) {
        startPage();
        List<ExamQuestion> list = examService.selectQuestionPage(question);
        return getDataTable(list);
    }

    /** 单题详情 */
    @GetMapping("/question/{questionId}")
    public AjaxResult question(@PathVariable Long questionId) {
        return AjaxResult.success(examService.getQuestion(questionId));
    }

    /** 材料详情 */
    @GetMapping("/material/{materialId}")
    public AjaxResult material(@PathVariable Long materialId) {
        return AjaxResult.success(examService.getMaterial(materialId));
    }

    /** 修改题目（补答案/解析） */
    @PutMapping("/question")
    public AjaxResult updateQuestion(@RequestBody ExamQuestion question) {
        return toAjax(examService.updateQuestion(question));
    }

    /** 新增题目 */
    @PostMapping("/question")
    public AjaxResult addQuestion(@RequestBody ExamQuestion question) {
        return toAjax(examService.addQuestion(question));
    }

    /** 新增试卷（自定义卷） */
    @PostMapping("/paper")
    public AjaxResult addPaper(@RequestBody ExamPaper paper) {
        if (examService.addPaper(paper) > 0) {
            return AjaxResult.success(paper.getId());
        }
        return AjaxResult.error("新增失败");
    }

    /** 随机刷题 */
    @GetMapping("/random")
    public AjaxResult random(String section, Integer count) {
        if (count == null || count <= 0 || count > 50) {
            count = 10;
        }
        return AjaxResult.success(examService.randomQuestions(section, count));
    }

    /** 提交答案 */
    @PostMapping("/record/save")
    public AjaxResult saveRecord(@RequestBody Map<String, Object> body) {
        Long questionId = Long.valueOf(String.valueOf(body.get("questionId")));
        String userAnswer = body.get("userAnswer") == null ? "" : String.valueOf(body.get("userAnswer"));
        Long userId = SecurityUtils.getUserId();
        return AjaxResult.success(examService.saveRecord(userId, questionId, userAnswer));
    }

    /** 某卷答题统计 */
    @GetMapping("/record/stats")
    public AjaxResult stats(Long paperId) {
        return AjaxResult.success(examService.paperStats(SecurityUtils.getUserId(), paperId));
    }

    /** 某卷已答题记录（断点续练） */
    @GetMapping("/record/answered")
    public AjaxResult answered(Long paperId) {
        return AjaxResult.success(examService.answeredRecords(SecurityUtils.getUserId(), paperId));
    }

    /** 错题本 */
    @GetMapping("/record/wrong")
    public AjaxResult wrongList() {
        return AjaxResult.success(examService.wrongList(SecurityUtils.getUserId()));
    }

    /** 移出错题本（删除该题答题记录） */
    @DeleteMapping("/record/{questionId}")
    public AjaxResult removeRecord(@PathVariable Long questionId) {
        return toAjax(examService.removeRecord(SecurityUtils.getUserId(), questionId));
    }

    /** 清空错题本 */
    @DeleteMapping("/record/wrong")
    public AjaxResult clearWrong() {
        return toAjax(examService.clearWrong(SecurityUtils.getUserId()));
    }

    /** 分模块答题统计（学习报告用） */
    @GetMapping("/record/section-stats")
    public AjaxResult sectionStats() {
        return AjaxResult.success(examService.sectionStats(SecurityUtils.getUserId()));
    }
}
