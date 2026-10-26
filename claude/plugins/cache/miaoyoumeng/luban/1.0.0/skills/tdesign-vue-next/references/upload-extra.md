# 上传（Upload）补充场景

## 适用场景

- 展示已有文件列表。
- 取消上传与失败处理。
- 读取服务端返回的文件 URL。
- 限制同时上传数量与展示进度。

本文只覆盖文件列表展示与上传实例交互。

## 文件列表展示

```vue
<template>
  <Upload v-model:files="fileList" action="/api/upload" theme="file-flow" multiple>
    <Button>上传文件</Button>
  </Upload>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Button, Upload } from "tdesign-vue-next";
import type { UploadFile } from "tdesign-vue-next";

const fileList = ref<UploadFile[]>([
  {
    name: "已有文件.pdf",
    url: "https://example.com/file.pdf",
    status: "success",
    size: 1024000,
  },
]);
</script>
```

已有文件通过 `v-model:files` 初始化。`status: "success"` 表示文件已上传完成，`url` 用于预览或下载。

## 取消上传

```ts
import type { UploadProps } from "tdesign-vue-next";

const controllers = new Map<string, AbortController>();

const customRequest: UploadProps["requestMethod"] = async (file) => {
  const controller = new AbortController();
  controllers.set(file.name, controller);

  try {
    const formData = new FormData();
    if (file.raw) formData.append("file", file.raw);

    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
      signal: controller.signal,
    });

    return { status: "success", response: await response.json() };
  } catch (error) {
    return {
      status: "fail",
      error: error instanceof Error ? error.message : "上传失败",
    };
  } finally {
    controllers.delete(file.name);
  }
};

const cancelUpload = (fileName: string) => {
  controllers.get(fileName)?.abort();
  controllers.delete(fileName);
};
```

每个文件使用独立的 `AbortController`，取消时按文件名中断对应请求，并在 `fail` 回调中提示用户。

## 读取服务端 URL

```ts
const onSuccess = (context: SuccessContext) => {
  if (context.response?.url) {
    context.file.url = context.response.url;
  }
};
```

服务端返回的 URL 写回文件对象，列表与预览才能使用。

## 数量与进度

- `max` 限制文件总数。
- `uploadAllFilesInOneRequest` 控制是否批量上传。
- 自定义请求时更新 `file.percent`，进度条才会变化。

```ts
file.percent = Math.round((loaded / total) * 100);
```

## 常见问题

### 上传进度不更新

自定义 `request-method` 时手动更新 `file.percent`；默认上传方式会自动更新。

### 文件数量超限没有提示

在 `before-upload` 中检查 `fileList.value.length` 是否达到 `max`，达到时提示并返回 `false`。

## 必须避免

- 不使用 `v-model:files`，却期望获取文件列表。
- `request-method` 返回非 Promise。
- 上传失败不给用户提示。
- 大文件不走分片上传。
- 在 `before-upload` 中执行耗时同步操作，阻塞选择文件。
