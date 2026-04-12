<template>
  <div id="app">
    <el-container class="main-container">
      <el-header class="app-header">
        <h1>黄金行情分析系统</h1>
        <nav class="nav-menu">
          <router-link to="/">仪表盘</router-link>
          <router-link to="/review">历史复盘</router-link>
        </nav>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #f5f7fa;
}

#app {
  min-height: 100vh;
}

.main-container {
  min-height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.app-header h1 {
  font-size: 1.5rem;
  font-weight: 600;
}

.nav-menu a {
  color: white;
  text-decoration: none;
  margin-left: 20px;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-menu a:hover,
.nav-menu a.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
}

.el-main {
  padding: 20px;
}
</style>