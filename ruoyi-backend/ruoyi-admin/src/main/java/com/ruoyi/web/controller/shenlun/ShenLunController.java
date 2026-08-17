package com.ruoyi.web.controller.shenlun;

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
import com.ruoyi.system.domain.ShenLunMaterial;
import com.ruoyi.system.domain.ShenLunPaper;
import com.ruoyi.system.domain.ShenLunQuestion;
import com.ruoyi.system.service.IShenLunService;

/** 申论刷题与题库管理 */
@RestController
@RequestMapping("/shenlun")
public class ShenLunController extends BaseController {

    @Autowired
    private IShenLunService shenLunService;

    /** 试卷列表（刷题） */
    @GetMapping("/paper/list")
    public AjaxResult listPapers(ShenLunPaper paper) {
        return AjaxResult.success(shenLunService.selectPaperList(paper));
    }

    /** 试卷管理分页 */
    @GetMapping("/paper/page")
    public TableDataInfo paperPage(ShenLunPaper paper) {
        startPage();
        List<ShenLunPaper> list = shenLunService.selectPaperPage(paper);
        return getDataTable(list);
    }

    /** 试卷详情（材料 + 题目） */
    @GetMapping("/paper/{paperId}")
    public AjaxResult paperDetail(@PathVariable Long paperId) {
        return AjaxResult.success(shenLunService.getPaperDetail(paperId));
    }

    /** 新增试卷 */
    @PostMapping("/paper")
    public AjaxResult addPaper(@RequestBody ShenLunPaper paper) {
        if (shenLunService.addPaper(paper) > 0) {
            return AjaxResult.success(paper.getId());
        }
        return AjaxResult.error("新增失败");
    }

    /** 修改试卷 */
    @PutMapping("/paper")
    public AjaxResult updatePaper(@RequestBody ShenLunPaper paper) {
        return toAjax(shenLunService.updatePaper(paper));
    }

    /** 删除试卷 */
    @DeleteMapping("/paper/{paperId}")
    public AjaxResult deletePaper(@PathVariable Long paperId) {
        return toAjax(shenLunService.deletePaper(paperId));
    }

    /** 材料详情 */
    @GetMapping("/material/{materialId}")
    public AjaxResult material(@PathVariable Long materialId) {
        return AjaxResult.success(shenLunService.getMaterial(materialId));
    }

    /** 新增材料 */
    @PostMapping("/material")
    public AjaxResult addMaterial(@RequestBody ShenLunMaterial material) {
        return toAjax(shenLunService.addMaterial(material));
    }

    /** 修改材料 */
    @PutMapping("/material")
    public AjaxResult updateMaterial(@RequestBody ShenLunMaterial material) {
        return toAjax(shenLunService.updateMaterial(material));
    }

    /** 删除材料 */
    @DeleteMapping("/material/{materialId}")
    public AjaxResult deleteMaterial(@PathVariable Long materialId) {
        return toAjax(shenLunService.deleteMaterial(materialId));
    }

    /** 题目详情 */
    @GetMapping("/question/{questionId}")
    public AjaxResult question(@PathVariable Long questionId) {
        return AjaxResult.success(shenLunService.getQuestion(questionId));
    }

    /** 新增题目 */
    @PostMapping("/question")
    public AjaxResult addQuestion(@RequestBody ShenLunQuestion question) {
        return toAjax(shenLunService.addQuestion(question));
    }

    /** 修改题目 */
    @PutMapping("/question")
    public AjaxResult updateQuestion(@RequestBody ShenLunQuestion question) {
        return toAjax(shenLunService.updateQuestion(question));
    }

    /** 删除题目 */
    @DeleteMapping("/question/{questionId}")
    public AjaxResult deleteQuestion(@PathVariable Long questionId) {
        return toAjax(shenLunService.deleteQuestion(questionId));
    }

    /** 提交作答（仅保存） */
    @PostMapping("/answer/submit")
    public AjaxResult submitAnswer(@RequestBody Map<String, Object> body) {
        Long paperId = Long.valueOf(String.valueOf(body.get("paperId")));
        String content = body.get("content") == null ? "{}" : String.valueOf(body.get("content"));
        Long id = shenLunService.submitAnswer(SecurityUtils.getUserId(), paperId, content);
        return AjaxResult.success(id);
    }

    /** 大模型评分 */
    @PostMapping("/answer/grade")
    public AjaxResult grade(@RequestBody Map<String, Object> body) {
        Long paperId = Long.valueOf(String.valueOf(body.get("paperId")));
        String content = body.get("content") == null ? "{}" : String.valueOf(body.get("content"));
        return AjaxResult.success(shenLunService.grade(SecurityUtils.getUserId(), paperId, content));
    }

    /** 我的申论作答记录 */
    @GetMapping("/answer/my")
    public AjaxResult myAnswers() {
        return AjaxResult.success(shenLunService.myAnswers(SecurityUtils.getUserId()));
    }

    /** 读取大模型配置 */
    @GetMapping("/llm-config")
    public AjaxResult getLlmConfig() {
        return AjaxResult.success(shenLunService.getLlmConfig());
    }

    /** 保存大模型配置 */
    @PostMapping("/llm-config")
    public AjaxResult saveLlmConfig(@RequestBody Map<String, String> cfg) {
        shenLunService.saveLlmConfig(cfg);
        return AjaxResult.success();
    }
}
