import json
from datetime import datetime

class DirectoryManagementAgent:
    def __init__(self):
        pass

    def generate_report(self, processed_records, metrics):
        """
        Generates a summary report of the validation process.
        """
        valid_count = sum(1 for r in processed_records if r['validation_status'] == 'Valid')
        flagged_count = sum(1 for r in processed_records if r['validation_status'] != 'Valid')
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_processed": len(processed_records),
            "valid_providers": valid_count,
            "flagged_providers": flagged_count,
            "accuracy_rate": metrics.get('accuracy', 0.0),
            "action_items": []
        }
        
        # Prioritize actions
        for record in processed_records:
            if record['confidence_score'] < 0.8:
                report['action_items'].append({
                    "provider": f"{record['record'].get('first_name')} {record['record'].get('last_name')}",
                    "issues": record.get('issues', []),
                    "priority": "High" if record['confidence_score'] < 0.5 else "Medium"
                })
                
        return report
