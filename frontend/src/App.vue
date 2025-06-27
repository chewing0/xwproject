<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">试验终端故障建模分析软件</div>
      <div class="nav-links">
        <router-link to="/module1">日志信令流程分析</router-link>
        <router-link to="/module2">模块二</router-link>
        <router-link to="/module3">知识图谱管理</router-link>
      </div>
    </nav>
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.navbar {
  background-color: #2c3e50;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand {
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-links {
  display: flex;
  gap: 1rem;
}

.nav-links a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-links a:hover {
  background-color: #34495e;
}

.nav-links a.router-link-active {
  background-color: #42b983;
}
</style>
