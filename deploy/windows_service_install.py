"""
Script d'installation du service Windows pour l'application TaskManager
"""
import os
import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import subprocess

class TaskManagerService(win32serviceutil.ServiceFramework):
    """Service Windows pour l'application TaskManager"""
    
    _svc_name_ = "PythonTaskManager"
    _svc_display_name_ = "Python Task Manager"
    _svc_description_ = "Service pour l'application de gestion de tâches Python"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
    
    def SvcStop(self):
        """Arrêt du service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
    
    def SvcDoRun(self):
        """Exécution du service"""
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()
    
    def main(self):
        """Point d'entrée principal"""
        # Déterminer le chemin de l'application
        app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(app_path)
        
        # Démarrer l'application avec Waitress
        cmd = [sys.executable, "-m", "waitress", 
               "--port=8000", 
               "--call", "run:main"]
        
        try:
            process = subprocess.Popen(cmd, cwd=app_path)
            process.wait()
        except Exception as e:
            servicemanager.LogErrorMsg(f"Erreur du service: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(TaskManagerService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(TaskManagerService)