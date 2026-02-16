import os
from datetime import datetime
from typing import Dict, List, Callable, Optional
from pathlib import Path
import loguru


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = loguru.logger
        
        self.jobs = {}
        self._scheduler = None
        self._setup_scheduler()
    
    def _setup_scheduler(self):
        """设置调度器"""
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.cron import CronTrigger
            
            self._scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
            self.logger.info("调度器初始化成功")
            
        except ImportError:
            self.logger.warning("APScheduler未安装，使用简单调度")
            self._scheduler = None
    
    def add_job(self, job_id: str, func: Callable, 
                trigger: str = 'cron', **kwargs):
        """添加任务"""
        
        if self._scheduler is None:
            self.jobs[job_id] = {
                'func': func,
                'trigger': trigger,
                'kwargs': kwargs
            }
            return
        
        try:
            if trigger == 'cron':
                trigger_obj = CronTrigger(**kwargs)
            elif trigger == 'interval':
                from apscheduler.triggers.interval import IntervalTrigger
                trigger_obj = IntervalTrigger(**kwargs)
            else:
                return
            
            self._scheduler.add_job(
                func, 
                trigger_obj, 
                id=job_id,
                **kwargs
            )
            
            self.logger.info(f"添加任务: {job_id}")
            
        except Exception as e:
            self.logger.error(f"添加任务失败 {job_id}: {e}")
    
    def start(self):
        """启动调度器"""
        if self._scheduler:
            self._scheduler.start()
            self.logger.info("调度器已启动")
    
    def stop(self):
        """停止调度器"""
        if self._scheduler:
            self._scheduler.shutdown()
            self.logger.info("调度器已停止")
    
    def pause_job(self, job_id: str):
        """暂停任务"""
        if self._scheduler:
            self._scheduler.pause_job(job_id)
            self.logger.info(f"暂停任务: {job_id}")
    
    def resume_job(self, job_id: str):
        """恢复任务"""
        if self._scheduler:
            self._scheduler.resume_job(job_id)
            self.logger.info(f"恢复任务: {job_id}")
    
    def remove_job(self, job_id: str):
        """删除任务"""
        if self._scheduler:
            self._scheduler.remove_job(job_id)
            self.logger.info(f"删除任务: {job_id}")
    
    def get_jobs(self) -> List[Dict]:
        """获取所有任务"""
        if self._scheduler:
            jobs = self._scheduler.get_jobs()
            return [
                {
                    'id': job.id,
                    'next_run': str(job.next_run_time) if job.next_run_time else None,
                    'name': job.name
                }
                for job in jobs
            ]
        return []
    
    def run_job_now(self, job_id: str):
        """立即运行任务"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            try:
                job['func']()
                self.logger.info(f"立即执行任务: {job_id}")
            except Exception as e:
                self.logger.error(f"执行任务失败 {job_id}: {e}")
        elif self._scheduler:
            job = self._scheduler.get_job(job_id)
            if job:
                job.func()
                self.logger.info(f"立即执行任务: {job_id}")
