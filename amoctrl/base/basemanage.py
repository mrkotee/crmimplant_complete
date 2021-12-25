from .models import AmoStatuses, create_session, PipelineStatuses


class AmoStatusesManage:

    def __init__(self, session=None, basepath=None):
        if session:
            self.session = session
        elif basepath:
            self.session = create_session(basepath)

    def get_all_leads(self):
        return self.session.query(AmoStatuses).all()

    def get_leads_dict(self):
        return {lead.amo_id: lead.status_id for lead in self.get_all_leads()}

    def update_changed_leads(self, leads_list):
        """

        :param leads_list: list with standart leads (with keys 'id', 'status_id')
        :return:
        """
        leads_in_base = self.get_all_leads()
        for lead in leads_list:
            lead_in_base = None
            for b_lead in leads_in_base:
                if b_lead.amo_id == lead['id']:
                    lead_in_base = b_lead
                    leads_in_base.remove(b_lead)
                    break
            if lead_in_base:
                lead_in_base.status_id = lead['status_id']
                self.session.commit()

    def add_new_leads(self, leads_list):
        leads_in_base = self.get_all_leads()
        for lead in leads_list:
            in_base = False
            for b_lead in leads_in_base:
                if b_lead.amo_id == lead['id']:
                    leads_in_base.remove(b_lead)
                    in_base = True
                    break
            if in_base:
                continue
            self.session.add(AmoStatuses(lead['id'], lead['status_id']))
            self.session.commit()

    def get_statuses(self):
        return self.session.query(PipelineStatuses).all()

    def get_status_sort_inx(self, status_id):
        return self.session.query(PipelineStatuses).filter(PipelineStatuses.status_id == status_id).first().sort_index

    def add_new_pipeline_statuses(self, pipelines_dict):
        statuses_in_base = self.get_statuses()
        for pipeline in pipelines_dict.values():
            for status in pipeline['statuses'].values():
                in_base = False
                for b_status in statuses_in_base:
                    if b_status.status_id == status['id']:
                        in_base = True
                        statuses_in_base.remove(b_status)
                        break
                if in_base:
                    continue
                self.session.add(PipelineStatuses(pipeline['id'], status['id'], status['name'], status['sort']))
                self.session.commit()


