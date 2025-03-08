<script setup lang="ts">
</script>

<template>
  <div class="layout">
    <!-- Header -->
    <header class="header">
      <h1>다시듣기 관리자</h1>
      <nav>
        <RouterLink to="/">영상 관리</RouterLink>
        <RouterLink to="/add">영상 등록</RouterLink>
      </nav>
    </header>

    <!-- Main Content -->
    <main class="main">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="footer">
      <p>&copy; 2025 Chzzk. All rights reserved.</p>
      <nav>
        <a href="#">Privacy Policy</a>
        <a href="#">Terms of Service</a>
        <a href="#">Contact Us</a>
      </nav>
    </footer>
  </div>
</template>

<style scoped>
/* 전체 레이아웃 */
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Header 스타일 */
.header {
  background: #ffffff;
  border-bottom: 1px solid #eee;
  padding: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.header h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.header nav {
  display: flex;
  gap: 20px;
}

.header a {
  text-decoration: none;
  color: #555;
  font-weight: 500;
  transition: color 0.2s;
}

.header a:hover {
  color: #007bff;
}

/* Main 스타일 */
.main {
  flex: 1;
  padding: 20px;
  background: #f9f9f9;
}

/* Footer 스타일 */
.footer {
  background: #333;
  color: #fff;
  padding: 20px;
  text-align: center;
  border-top: 1px solid #444;
}

.footer p {
  margin: 0 0 10px;
  font-size: 14px;
}

.footer nav {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.footer a {
  color: #ccc;
  text-decoration: none;
  font-size: 12px;
  transition: color 0.2s;
}

.footer a:hover {
  color: #fff;
}
</style>