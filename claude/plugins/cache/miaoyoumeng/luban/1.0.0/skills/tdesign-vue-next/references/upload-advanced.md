# 上传（Upload）复杂场景

## 适用场景

- 受控文件列表。
- 自定义上传请求。
- 上传前校验。
- 图片尺寸与格式校验。
- 拖拽上传。
- 分片上传与断点续传。
- 手动触发上传。

简单上传使用 `Upload` + `action` + `v-model:files` 即可。

## 受控文件列表

```vue
<template>
  <Upload
    v-model:files="fileList"
    action="/api/upload"
    :max="5"
    @success="onSuccess"
    @fail="onFail"
    @remove="onRemove"
  >
    <Button>点击上传</Button>
  </Upload>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Button, Upload } from "tdesign-vue-next";
import type { SuccessContext, UploadFile, UploadRemoveContext } from "tdesign-vue-next";

const fileList = ref<UploadFile[]>([]);

const onSuccess = (context: SuccessContext) => {
  const { file, response } = context;
  if (response?.url) {
    file.url = response.url;
  }
};

const onFail = (context: { file: UploadFile; error: Error }) => {
  console.error("上传失败", context.error);
};

const onRemove = (context: UploadRemoveContext) => {
  console.log("移除文件", context.file);
};
</script>
```

必须使用 `v-model:files` 才能读取和修改文件列表。

## 自定义上传请求

```vue
<template>
  <Upload v-model:files="fileList" :request-method="customRequest">
    <Button>自定义上传</Button>
  </Upload>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Button, Upload } from "tdesign-vue-next";
import type { RequestMethodResponse, UploadFile, UploadProps } from "tdesign-vue-next";

const fileList = ref<UploadFile[]>([]);

const customRequest: UploadProps["requestMethod"] = async (file) => {
  if (!file.raw) {
    return { status: "fail", error: "文件为空" };
  }

  const formData = new FormData();
  formData.append("file", file.raw);
  formData.append("name", file.name);

  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token") ?? ""}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return {
      status: "success",
      response: { url: data.url, ...data },
    } as RequestMethodResponse;
  } catch (error) {
    return {
      status: "fail",
      error: error instanceof Error ? error.message : "上传失败",
    } as RequestMethodResponse;
  }
};
</script>
```

`request-method` 必须返回 `Promise`，否则组件无法正确更新上传状态。

## 上传前校验

```vue
<template>
  <Upload
    v-model:files="fileList"
    action="/api/upload"
    :before-upload="beforeUpload"
    :size-limit="{ size: 10, unit: 'MB' }"
    accept="image/*,.pdf"
  >
    <Button>上传文件</Button>
    <template #tips>
      <div class="tips">支持 jpg、png、pdf，单个文件不超过 10MB</div>
    </template>
  </Upload>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Button, MessagePlugin, Upload } from "tdesign-vue-next";
import type { UploadFile, UploadProps } from "tdesign-vue-next";

const fileList = ref<UploadFile[]>([]);

const beforeUpload: UploadProps["beforeUpload"] = (file) => {
  const allowedTypes = ["image/jpeg", "image/png", "application/pdf"];

  if (!allowedTypes.includes(file.type)) {
    MessagePlugin.error("不支持的文件类型");
    return false;
  }

  if (file.name.length > 100) {
    MessagePlugin.error("文件名过长");
    return false;
  }

  return true;
};
</script>
```

`before-upload` 返回 `false` 阻止上传，返回 `true` 放行，返回 `File` 可替换文件。

## 图片尺寸校验

```vue
<script setup lang="ts">
import { MessagePlugin } from "tdesign-vue-next";
import type { UploadProps } from "tdesign-vue-next";

const validateImage: UploadProps["beforeUpload"] = (file) => {
  return new Promise((resolve) => {
    if (!file.raw) {
      resolve(false);
      return;
    }

    const image = new Image();
    image.src = URL.createObjectURL(file.raw);

    image.onload = () => {
      URL.revokeObjectURL(image.src);

      if (image.width < 200 || image.height < 200) {
        MessagePlugin.error("图片尺寸不能小于 200x200");
        resolve(false);
        return;
      }

      const ratio = image.width / image.height;
      if (ratio < 0.5 || ratio > 2) {
        MessagePlugin.error("图片宽高比需在 1:2 到 2:1 之间");
        resolve(false);
        return;
      }

      resolve(true);
    };

    image.onerror = () => {
      MessagePlugin.error("无法读取图片");
      resolve(false);
    };
  });
};
</script>
```

## 拖拽上传

```vue
<template>
  <Upload v-model:files="fileList" action="/api/upload" theme="custom" drag multiple>
    <template #dragContent="{ dragActive }">
      <div :class="['drag-area', { active: dragActive }]">
        <UploadIcon size="48" />
        <p v-if="dragActive">释放鼠标上传</p>
        <p v-else>点击或拖拽文件到此区域上传</p>
      </div>
    </template>
  </Upload>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Upload } from "tdesign-vue-next";
import { UploadIcon } from "tdesign-icons-vue-next";
import type { UploadFile } from "tdesign-vue-next";

const fileList = ref<UploadFile[]>([]);
</script>

<style scoped>
.drag-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 200px;
  border: 2px dashed var(--td-border-level-2-color);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.drag-area:hover,
.drag-area.active {
  border-color: var(--td-brand-color);
}

.drag-area p {
  margin-top: 8px;
  color: var(--td-text-color-secondary);
}
</style>
```

## 分片上传

```vue
<script setup lang="ts">
import { ref } from "vue";
import type { RequestMethodResponse, UploadFile, UploadProps } from "tdesign-vue-next";

const fileList = ref<UploadFile[]>([]);
const CHUNK_SIZE = 5 * 1024 * 1024;

const chunkUpload: UploadProps["requestMethod"] = async (file) => {
  if (!file.raw) {
    return { status: "fail", error: "文件为空" };
  }

  const raw = file.raw;
  const totalChunks = Math.ceil(raw.size / CHUNK_SIZE);
  const fileHash = `${raw.name}-${raw.size}-${raw.lastModified}`;

  try {
    const checkResponse = await fetch(`/api/upload/check?hash=${encodeURIComponent(fileHash)}`);
    const { uploadedChunks } = await checkResponse.json();

    for (let index = 0; index < totalChunks; index += 1) {
      if (uploadedChunks.includes(index)) continue;

      const start = index * CHUNK_SIZE;
      const end = Math.min(start + CHUNK_SIZE, raw.size);
      const formData = new FormData();
      formData.append("chunk", raw.slice(start, end));
      formData.append("hash", fileHash);
      formData.append("index", String(index));
      formData.append("total", String(totalChunks));

      const chunkResponse = await fetch("/api/upload/chunk", {
        method: "POST",
        body: formData,
      });

      if (!chunkResponse.ok) {
        throw new Error(`分片 ${index} 上传失败`);
      }

      file.percent = Math.round(((index + 1) / totalChunks) * 100);
    }

    const mergeResponse = await fetch("/api/upload/merge", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ hash: fileHash, name: raw.name, total: totalChunks }),
    });
    const { url } = await mergeResponse.json();

    return { status: "success", response: { url } } as RequestMethodResponse;
  } catch (error) {
    return {
      status: "fail",
      error: error instanceof Error ? error.message : "上传失败",
    } as RequestMethodResponse;
  }
};
</script>
```

生产环境用 Web Worker 计算文件 hash，示例中的 hash 仅用于演示断点续传流程。

## 手动触发上传

```vue
<template>
  <Space direction="vertical">
    <Upload
      ref="uploadRef"
      v-model:files="fileList"
      action="/api/upload"
      :auto-upload="false"
      multiple
    >
      <Button>选择文件</Button>
    </Upload>
    <Button theme="primary" @click="startUpload">开始上传</Button>
  </Space>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Button, Space, Upload } from "tdesign-vue-next";
import type { UploadFile, UploadInstanceFunctions } from "tdesign-vue-next";

const fileList = ref<UploadFile[]>([]);
const uploadRef = ref<UploadInstanceFunctions>();

const startUpload = () => {
  uploadRef.value?.uploadFiles();
};
</script>
```
