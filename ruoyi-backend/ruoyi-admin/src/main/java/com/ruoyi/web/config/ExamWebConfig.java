package com.ruoyi.web.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * 题库图片静态资源映射：/exam-img/** -> 本地图片目录
 */
@Configuration
public class ExamWebConfig implements WebMvcConfigurer {

    @Value("${exam.image-path}")
    private String imagePath;

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/exam-img/**")
                .addResourceLocations("file:" + imagePath)
                .addResourceLocations("file:" + imagePath + "sydw/")
                .addResourceLocations("file:" + imagePath.replace("images/", "images_sydw/"));
    }
}
