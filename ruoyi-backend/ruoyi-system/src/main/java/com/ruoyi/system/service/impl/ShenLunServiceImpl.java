package com.ruoyi.system.service.impl;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;
import com.ruoyi.system.domain.ShenLunAnswer;
import com.ruoyi.system.domain.ShenLunMaterial;
import com.ruoyi.system.domain.ShenLunPaper;
import com.ruoyi.system.domain.ShenLunQuestion;
import com.ruoyi.system.mapper.ShenLunMapper;
import com.ruoyi.system.service.IShenLunService;

/** 申论题库服务实现 */
@Service
public class ShenLunServiceImpl implements IShenLunService {

    private static final Logger log = LoggerFactory.getLogger(ShenLunServiceImpl.class);

    @Autowired
    private ShenLunMapper shenLunMapper;

    private String llmConfigPath() {
        String dir = System.getProperty("user.dir");
        return dir + File.separator + "data" + File.separator + "llm_config.json";
    }

    @Override
    public List<ShenLunPaper> selectPaperList(ShenLunPaper paper) {
        return shenLunMapper.selectPaperList(paper);
    }

    @Override
    public List<ShenLunPaper> selectPaperPage(ShenLunPaper paper) {
        return shenLunMapper.selectPaperPage(paper);
    }

    @Override
    public Map<String, Object> getPaperDetail(Long paperId) {
        Map<String, Object> result = new HashMap<>();
        result.put("paper", shenLunMapper.selectPaperById(paperId));
        result.put("materials", shenLunMapper.selectMaterialsByPaperId(paperId));
        result.put("questions", shenLunMapper.selectQuestionsByPaperId(paperId));
        return result;
    }

    @Override
    public int addPaper(ShenLunPaper paper) {
        if (paper.getPaperCode() == null || paper.getPaperCode().isEmpty()) {
            paper.setPaperCode("sl-" + System.currentTimeMillis());
        }
        if (paper.getQuestionCount() == null) {
            paper.setQuestionCount(0);
        }
        return shenLunMapper.insertPaper(paper);
    }

    @Override
    public int updatePaper(ShenLunPaper paper) {
        return shenLunMapper.updatePaper(paper);
    }

    @Override
    public int deletePaper(Long paperId) {
        shenLunMapper.deleteMaterialsByPaperId(paperId);
        shenLunMapper.deleteQuestionsByPaperId(paperId);
        return shenLunMapper.deletePaper(paperId);
    }

    @Override
    public ShenLunMaterial getMaterial(Long materialId) {
        return shenLunMapper.selectMaterialById(materialId);
    }

    @Override
    public int addMaterial(ShenLunMaterial material) {
        if (material.getTitle() == null || material.getTitle().isEmpty()) {
            material.setTitle("材料" + material.getMNo());
        }
        return shenLunMapper.insertMaterial(material);
    }

    @Override
    public int updateMaterial(ShenLunMaterial material) {
        return shenLunMapper.updateMaterial(material);
    }

    @Override
    public int deleteMaterial(Long materialId) {
        return shenLunMapper.deleteMaterial(materialId);
    }

    @Override
    public ShenLunQuestion getQuestion(Long questionId) {
        return shenLunMapper.selectQuestionById(questionId);
    }

    @Override
    public int addQuestion(ShenLunQuestion question) {
        if (question.getQno() == null) {
            List<ShenLunQuestion> list = shenLunMapper.selectQuestionsByPaperId(question.getPaperId());
            question.setQno(list.size() + 1);
        }
        int n = shenLunMapper.insertQuestion(question);
        refreshPaperCount(question.getPaperId());
        return n;
    }

    @Override
    public int updateQuestion(ShenLunQuestion question) {
        int n = shenLunMapper.updateQuestion(question);
        if (question.getPaperId() != null) {
            refreshPaperCount(question.getPaperId());
        }
        return n;
    }

    @Override
    public int deleteQuestion(Long questionId) {
        ShenLunQuestion q = shenLunMapper.selectQuestionById(questionId);
        int n = shenLunMapper.deleteQuestion(questionId);
        if (q != null && q.getPaperId() != null) {
            refreshPaperCount(q.getPaperId());
        }
        return n;
    }

    private void refreshPaperCount(Long paperId) {
        ShenLunPaper p = shenLunMapper.selectPaperById(paperId);
        if (p != null) {
            p.setQuestionCount(shenLunMapper.selectQuestionsByPaperId(paperId).size());
            shenLunMapper.updatePaper(p);
        }
    }

    @Override
    public Long submitAnswer(Long userId, Long paperId, String content) {
        ShenLunAnswer a = new ShenLunAnswer();
        a.setUserId(userId);
        a.setPaperId(paperId);
        a.setContent(content);
        a.setStatus(0);
        shenLunMapper.insertAnswer(a);
        return a.getId();
    }

    @Override
    public Map<String, Object> grade(Long userId, Long paperId, String content) {
        Map<String, Object> result = new HashMap<>();
        String apiKey = System.getenv("DEEPSEEK_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            result.put("success", false);
            result.put("msg", "未配置环境变量 DEEPSEEK_API_KEY，请联系管理员配置");
            return result;
        }
        List<ShenLunQuestion> questions = shenLunMapper.selectQuestionsByPaperId(paperId);
        JSONObject contentJson;
        try {
            contentJson = JSON.parseObject(content);
        } catch (Exception e) {
            contentJson = new JSONObject();
        }
        // 构造评分请求
        StringBuilder sb = new StringBuilder();
        sb.append("你是资深公务员考试申论阅卷专家。请严格按照国考申论评分标准，参考给定参考答案，对考生的每道题作答进行评分和点评。\n\n");
        for (ShenLunQuestion q : questions) {
            sb.append("【第").append(q.getQno()).append("题】（满分").append(q.getScore()).append("分，字数要求")
              .append(q.getWordLimit() != null ? q.getWordLimit() : "").append("字）\n");
            sb.append("题目：").append(q.getTitle()).append("\n");
            sb.append("参考答案要点：").append(q.getRefAnswer() == null ? "（无）" : q.getRefAnswer()).append("\n");
            String mine = contentJson.getString(String.valueOf(q.getQno()));
            sb.append("考生作答：").append(mine == null || mine.isEmpty() ? "（未作答）" : mine).append("\n\n");
        }
        sb.append("请对每一题输出评分结果，严格输出 JSON 数组，不要输出其他内容，格式：");
        sb.append("[{\"qno\":1,\"score\":12,\"maxScore\":15,\"analysis\":\"得分点分析（结合参考要点逐条说明得扣分原因）\",\"suggestions\":\"改进建议（具体可操作）\"}]");
        String prompt = sb.toString();
        try {
            String resp = callLlm(apiKey, prompt);
            JSONArray grades = JSON.parseArray(extractJsonArray(resp));
            int total = 0;
            int max = 0;
            for (int i = 0; i < grades.size(); i++) {
                JSONObject g = grades.getJSONObject(i);
                total += g.getIntValue("score");
                max += g.getIntValue("maxScore");
            }
            JSONObject gradeResult = new JSONObject();
            gradeResult.put("grades", grades);
            gradeResult.put("totalScore", total);
            gradeResult.put("maxScore", max);
            // 保存
            ShenLunAnswer a = new ShenLunAnswer();
            a.setUserId(userId);
            a.setPaperId(paperId);
            a.setContent(content);
            a.setGradeJson(gradeResult.toJSONString());
            a.setStatus(1);
            shenLunMapper.insertAnswer(a);
            result.put("success", true);
            result.put("grade", gradeResult);
            result.put("answerId", a.getId());
        } catch (Exception e) {
            log.error("申论评分失败", e);
            result.put("success", false);
            result.put("msg", "评分失败：" + e.getMessage());
        }
        return result;
    }

    private String callLlm(String apiKey, String prompt) throws Exception {
        // Anthropic 兼容端点（DeepSeek: https://api.deepseek.com/anthropic）
        String base = System.getenv("DEEPSEEK_BASE_URL");
        if (base == null || base.isEmpty()) {
            base = "https://api.deepseek.com/anthropic";
        }
        String model = System.getenv("DEEPSEEK_MODEL");
        if (model == null || model.isEmpty()) {
            model = "deepseek-v4-flash";
        }
        if (base.endsWith("/")) {
            base = base.substring(0, base.length() - 1);
        }
        URL url = new URL(base + "/v1/messages");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setConnectTimeout(60000);
        conn.setReadTimeout(240000);
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setRequestProperty("x-api-key", apiKey);
        conn.setRequestProperty("anthropic-version", "2023-06-01");
        conn.setDoOutput(true);
        JSONObject body = new JSONObject();
        body.put("model", model);
        body.put("max_tokens", 4096);
        body.put("system", "你是资深的公务员考试申论阅卷专家，评分严谨、点评专业，只输出 JSON。");
        JSONArray msgs = new JSONArray();
        JSONObject user = new JSONObject();
        user.put("role", "user");
        user.put("content", prompt);
        msgs.add(user);
        body.put("messages", msgs);
        try (OutputStream os = conn.getOutputStream()) {
            os.write(body.toJSONString().getBytes(StandardCharsets.UTF_8));
        }
        int code = conn.getResponseCode();
        BufferedReader br = new BufferedReader(new InputStreamReader(
                code >= 400 ? conn.getErrorStream() : conn.getInputStream(), StandardCharsets.UTF_8));
        StringBuilder resp = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            resp.append(line);
        }
        br.close();
        if (code >= 400) {
            throw new RuntimeException("大模型接口返回 " + code + ": " + resp);
        }
        JSONObject jo = JSON.parseObject(resp.toString());
        JSONArray contentArr = jo.getJSONArray("content");
        StringBuilder text = new StringBuilder();
        for (int i = 0; i < contentArr.size(); i++) {
            JSONObject c = contentArr.getJSONObject(i);
            if ("text".equals(c.getString("type"))) {
                text.append(c.getString("text"));
            }
        }
        return text.toString();
    }

    private String extractJsonArray(String s) {
        int a = s.indexOf('[');
        int b = s.lastIndexOf(']');
        if (a >= 0 && b > a) {
            return s.substring(a, b + 1);
        }
        return s;
    }

    @Override
    public List<Map<String, Object>> myAnswers(Long userId) {
        return shenLunMapper.selectAnswersByUser(userId);
    }

    @Override
    public Map<String, String> getLlmConfig() {
        // 配置一律来自环境变量（不落盘、不暴露）
        Map<String, String> cfg = new HashMap<>();
        cfg.put("baseUrl", System.getenv("DEEPSEEK_BASE_URL") != null ? System.getenv("DEEPSEEK_BASE_URL") : "https://api.deepseek.com/anthropic");
        cfg.put("model", System.getenv("DEEPSEEK_MODEL") != null ? System.getenv("DEEPSEEK_MODEL") : "deepseek-v4-flash");
        String key = System.getenv("DEEPSEEK_API_KEY");
        cfg.put("apiKeySet", key != null && !key.isEmpty() ? "1" : "0");
        return cfg;
    }

    @Override
    public void saveLlmConfig(Map<String, String> cfg) {
        throw new RuntimeException("AI 评分配置通过服务器环境变量设置（DEEPSEEK_API_KEY / DEEPSEEK_BASE_URL / DEEPSEEK_MODEL），不支持页面修改");
    }
}
