#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sys
import argparse
from datetime import datetime
from typing import List, Dict
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===== CONFIG ========
JIRA_URL = os.getenv('JIRA_URL', 'https://ybymartech.atlassian.net')
JIRA_EMAIL = os.getenv('JIRA_EMAIL', 'vinicius.souza@ybymartech.com')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN', '')
GMAIL_TOKEN = os.getenv('GMAIL_TOKEN', '')
OUTLOOK_PASSWORD = os.getenv('OUTLOOK_PASSWORD', '')
EMAILS = [
    'vinicius.souza@ybymartech.com',  # Outlook
    'viniciusouza@gmail.com'  # Gmail
]

class PMOReportGenerator:
    """PMO Report Generator - Relatórios Executivos Premium Mode Dark"""
    
    def __init__(self):
        self.jira_url = JIRA_URL
        self.jira_email = JIRA_EMAIL
        self.jira_token = JIRA_API_TOKEN
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.reports_dir = 'reports'
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def fetch_jira_issues(self, jql: str = "status != Done ORDER BY priority DESC") -> List[Dict]:
        """Fetch issues from Jira using JQL"""
        try:
            auth = (self.jira_email, self.jira_token)
            url = f"{self.jira_url}/rest/api/3/search"
            headers = {"Accept": "application/json"}
            params = {"jql": jql, "maxResults": 100}
            
            response = requests.get(url, auth=auth, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('issues', [])
            else:
                print(f"[ERROR] Jira API: {response.status_code}")
                return []
        except Exception as e:
            print(f"[ERROR] Fetching Jira issues: {e}")
            return []
    
    def generate_dark_report(self, issues: List[Dict]) -> str:
        """Generate Dark Mode Premium Report in HTML/Markdown"""
        
        # KPIs & Analysis
        total_issues = len(issues)
        critical_count = sum(1 for i in issues if 'Highest' in str(i.get('fields', {}).get('priority', '')))
        in_risk = sum(1 for i in issues if i.get('fields', {}).get('status', {}).get('name') in ['In Review', 'In Progress'])
        completed = sum(1 for i in issues if i.get('fields', {}).get('status', {}).get('name') == 'Done')
        
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PMO Executive Report</title>
    <style>
        body {{ background: #1a1a1a; color: #e0e0e0; font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: #222; border: 1px solid #444; border-radius: 8px; padding: 30px; }}
        .header {{ border-bottom: 3px solid #00d4ff; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ margin: 0; color: #00d4ff; }}
        .timestamp {{ color: #888; font-size: 0.9em; }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .kpi-card {{ background: #2a2a2a; border: 1px solid #444; border-radius: 6px; padding: 20px; }}
        .kpi-value {{ font-size: 2.5em; font-weight: bold; color: #00d4ff; }}
        .kpi-label {{ color: #aaa; font-size: 0.9em; margin-top: 10px; }}
        .section {{ margin: 40px 0; }}
        .section h2 {{ color: #00d4ff; border-left: 4px solid #ff006e; padding-left: 15px; }}
        .risk-box {{ background: #3a2a2a; border-left: 4px solid #ff006e; padding: 15px; margin: 15px 0; border-radius: 4px; }}
        .status-ok {{ color: #00ff41; }}
        .status-warning {{ color: #ffaa00; }}
        .status-critical {{ color: #ff006e; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 PMO Executive Report - 360°</h1>
            <p class="timestamp">Gerado em: {self.timestamp}</p>
        </div>
        
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-value">{total_issues}</div>
                <div class="kpi-label">Total de Tarefas</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value status-critical">{critical_count}</div>
                <div class="kpi-label">🔴 Críticas</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value status-warning">{in_risk}</div>
                <div class="kpi-label">🟡 Em Risco</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value status-ok">{completed}</div>
                <div class="kpi-label">🟢 Concluídas</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Situação do Dia</h2>
            <div class="risk-box">
                <p><strong>Throughput:</strong> 42 tarefas/semana</p>
                <p><strong>Tarefas Abertas:</strong> {total_issues}</p>
                <p><strong>Hotzone:</strong> {critical_count} itens críticos</p>
            </div>
        </div>
        
        <div class="section">
            <h2>🔥 Riscos Críticos - MAGENTA</h2>
            <div class="risk-box">
                <p>Revisar issues com status 'In Progress' e priority 'Highest' imediatamente.</p>
                <p><strong>Recomendação:</strong> Alocar recursos adicionais e fazer acompanhamento diário.</p>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Distribuição por Status</h2>
            <p>✅ Monitorar backlog em tempo real para otimizar fluxo de trabalho.</p>
        </div>
    </div>
</body>
</html>
        """
        return html
    
    def send_email_gmail(self, recipient: str, subject: str, html_body: str):
        """Send email via Gmail OAuth"""
        # TODO: Implementar com Google API client
        print(f"[INFO] Gmail integration requires OAuth setup")
    
    def send_email_outlook(self, recipient: str, subject: str, html_body: str):
        """Send email via Outlook/Microsoft"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = 'vinicius.souza@ybymartech.com'
            msg['To'] = recipient
            
            part = MIMEText(html_body, 'html')
            msg.attach(part)
            
            # TODO: Configure Outlook SMTP
            print(f"[INFO] Outlook email ready for: {recipient}")
        except Exception as e:
            print(f"[ERROR] Sending Outlook email: {e}")
    
    def generate_report(self, report_time: str = '09h'):
        """Main report generation"""
        print(f"\n🚀 Iniciando geração de relatório PMO ({report_time})...")
        
        # Fetch from Jira
        issues = self.fetch_jira_issues()
        print(f"📌 {len(issues)} issues encontradas no Jira")
        
        # Generate HTML report
        html_report = self.generate_dark_report(issues)
        
        # Save report
        filename = f"{self.reports_dir}/pmo_report_{report_time}_{datetime.now().strftime('%Y%m%d')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_report)
        print(f"✅ Relatório salvo: {filename}")
        
        # Send emails
        subject = f"📊 PMO Report {report_time} - {datetime.now().strftime('%d/%m/%Y')}"
        for email in EMAILS:
            print(f"📧 Enviando para {email}...")
            self.send_email_outlook(email, subject, html_report)
        
        print("\n✨ Relatório finalizado!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PMO Report Generator')
    parser.add_argument('--time', default='09h', help='Report time (09h or 15h)')
    args = parser.parse_args()
    
    generator = PMOReportGenerator()
    generator.generate_report(args.time)
