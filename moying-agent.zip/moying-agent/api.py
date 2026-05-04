from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pipeline import MoyingAgent
import uvicorn
import threading

app = FastAPI(title="墨影Agent API", description="网文全流程自动化创作API服务", version="1.0.0")

# 跨域支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局任务状态（线程安全）
task_status = {"running": False, "message": "系统就绪", "current_chapter": 0, "total_chapters": 0}
status_lock = threading.Lock()

class StartRequest(BaseModel):
    core_idea: str
    platform: str = "fanqie"

def run_agent_task(core_idea: str, platform: str):
    """后台运行Agent任务"""
    global task_status
    with status_lock:
        task_status = {"running": True, "message": "初始化Dramatica故事骨架", "current_chapter": 0, "total_chapters": 0}
    
    try:
        agent = MoyingAgent()
        agent.run_dramatica_flow(core_idea, platform)
        
        with status_lock:
            task_status = {"running": False, "message": "✅ 全流程执行完成", "current_chapter": 0, "total_chapters": 0}
    except Exception as e:
        with status_lock:
            task_status = {"running": False, "message": f"❌ 执行失败: {str(e)}", "current_chapter": 0, "total_chapters": 0}

@app.get("/", summary="健康检查")
def health_check():
    return {"status": "ok", "name": "墨影Agent", "version": "1.0.0"}

@app.post("/api/start", summary="启动创作流程")
def start_agent(req: StartRequest, background_tasks: BackgroundTasks):
    with status_lock:
        if task_status["running"]:
            return {"code": 400, "msg": "任务正在运行中，请等待完成", "data": task_status}
    
    background_tasks.add_task(run_agent_task, req.core_idea, req.platform)
    return {"code": 200, "msg": "任务已启动", "data": task_status}

@app.get("/api/status", summary="查询任务状态")
def get_task_status():
    with status_lock:
        return {"code": 200, "data": task_status}

@app.post("/api/stop", summary="停止任务")
def stop_agent():
    global task_status
    with status_lock:
        if not task_status["running"]:
            return {"code": 400, "msg": "没有正在运行的任务"}
        
        task_status = {"running": False, "message": "⏹️ 任务已手动停止", "current_chapter": 0, "total_chapters": 0}
        return {"code": 200, "msg": "任务已停止", "data": task_status}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)