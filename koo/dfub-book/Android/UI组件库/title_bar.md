## 标题栏

概述

提供标准的通用标题栏

配置

```xml
 <attr name="UITitleBarConfigStyle" format="reference" />
```

配置Attr

```xml
<!--标题栏配置参数-->
    <declare-styleable name="UITitleBarConfig">
        <!--标题栏左边边距-->
        <attr name="title_bar_config_left_padding" format="dimension" />
        <!--标题栏右边边距-->
        <attr name="title_bar_config_right_padding" format="dimension" />
        <!--标题栏高度-->
        <attr name="title_bar_config_height" format="dimension" />
        <!--正常标题栏返回图标-->
        <attr name="title_bar_config_common_style_back_icon" format="reference" />
        <!--正常标题栏背景颜色-->
        <attr name="title_bar_config_common_style_background" format="color" />
        <!--正常标题栏文字颜色-->
        <attr name="title_bar_config_common_text_color" format="color" />
        <!--透明标题栏返回图标-->
        <attr name="title_bar_config_transparent_style_back_icon" format="reference" />
        <!--透明状态栏背景颜色-->
        <attr name="title_bar_config_transparent_background" format="color" />
        <!--透明标题栏文字颜色-->
        <attr name="title_bar_config_transparent_text_color" format="color" />
        <!--左侧文字图片与文字的间距-->
        <attr name="title_bar_config_left_view_drawable_padding" format="dimension" />
        <!--右侧文字图片与文字的间距-->
        <attr name="title_bar_config_right_view_drawable_padding" format="dimension" />
        <!--标题左右边距-->
        <attr name="title_bar_config_title_text_margin" format="dimension" />
        <!--标题是否加粗-->
        <attr name="title_bar_config_title_text_bold" format="boolean" />
    </declare-styleable>
```

样式

```xml
 <attr name="UITitleBarViewStyle" format="reference" />
```

样式Attr

```xml
 <!--标题栏-->
    <declare-styleable name="UITitleBarView">
        <!-- 整体样式 -->
        <attr name="title_bar_style">
            <!--默认样式-->
            <enum name="common" value="0x10" />
            <!--透明样式-->
            <enum name="transparent" value="0x20" />
        </attr>
        <!-- 中间标题 -->
        <attr name="title_bar_content_title" format="string" />
        <!--中间标题颜色-->
        <attr name="title_bar_content_title_color" format="color" />
        <!--中间标题字体大小-->
        <attr name="title_bar_content_title_size" format="dimension" />
        <!-- 左边文字 -->
        <attr name="title_bar_left_title" format="string" />
        <!-- leftIcon 优先于 backButton -->
        <attr name="title_bar_left_icon" format="reference" />
        <!-- 返回按钮（默认开） -->
        <attr name="title_bar_back_button" format="boolean" />
        <!--左边标题文字颜色-->
        <attr name="title_bar_left_color" format="color" />
        <!--左边标题文字大小-->
        <attr name="title_bar_left_size" format="dimension" />
        <!--左边区域背景颜色-->
        <attr name="title_bar_left_background" format="reference|color" />
        <!-- 右边文字 -->
        <attr name="title_bar_right_title" format="string" />
        <!--右边图标-->
        <attr name="title_bar_right_icon" format="reference" />
        <!--右边文字颜色-->
        <attr name="title_bar_right_color" format="color" />
        <!--右边文字大小-->
        <attr name="title_bar_right_size" format="dimension" />
        <!--右边区域背景颜色-->
        <attr name="title_bar_right_background" format="reference|color" />
        <!-- 分割线 -->
        <attr name="title_bar_line_visible" format="boolean" />
        <!--分割线的颜色-->
        <attr name="title_bar_line_color" format="reference|color" />
        <!--分割线的高度-->
        <attr name="title_bar_line_size" format="dimension" />
    </declare-styleable>
```

示例

```xml
 <com.xdf.dfub.ui.titlebar.UITitleBarView
        android:id="@+id/mUITitleBarView1"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_gravity="center_vertical"
        android:layout_marginTop="16dp"
        app:title_bar_content_title="左右常见样式"
        app:title_bar_left_title="左边文字"
        app:title_bar_right_icon="@drawable/ic_baseline_search_24"
        app:title_bar_style="common" />
```

