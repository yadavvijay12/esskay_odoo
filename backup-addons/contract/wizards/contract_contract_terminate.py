# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractContractTerminate(models.TransientModel):

    _name = "contract.contract.terminate"
    _description = "Terminate Contract Wizard"

    contract_id = fields.Many2one(
        comodel_name="contract.contract",
        string="Contract",
        required=True,
        ondelete="cascade",
    )
    terminate_reason_id = fields.Many2one(
        comodel_name="contract.terminate.reason",
        string="Reason",
        required=True,
        ondelete="cascade",
    )
    terminate_comment = fields.Text(string="Comment")
    terminate_date = fields.Date(string="Date", required=True)
    terminate_comment_required = fields.Boolean(
        related="terminate_reason_id.terminate_comment_required"
    )
    is_renewal = fields.Boolean('Is this renewal Contract?')
    is_cancel = fields.Boolean('Is this cancel Contract?')
    is_required_approval = fields.Boolean('Require Approval')
    approval_request_id = fields.Many2one(string="Approval", comodel_name="multi.approval.type")

    def terminate_contract(self):
        for wizard in self:
            if self.is_renewal:
                if self.is_required_approval:
                    send_for_approval = True
                    approval_request_id = self.approval_request_id
                    wizard.contract_id.with_context(is_renewal=True,send_for_approval=True, approval_request_id=self.approval_request_id,contract_id=self.contract_id)._terminate_contract(
                        wizard.terminate_reason_id,
                        wizard.terminate_comment,
                        wizard.terminate_date,
                    )
                else:
                    wizard.contract_id.with_context(is_renewal=True)._terminate_contract(
                        wizard.terminate_reason_id,
                        wizard.terminate_comment,
                        wizard.terminate_date,
                    )
            elif self.is_cancel:
                if self.is_required_approval:
                    send_for_approval = True
                    approval_request_id = self.approval_request_id
                    wizard.contract_id.with_context(is_cancel=True,send_for_approval=True, approval_request_id=self.approval_request_id,contract_id=self.contract_id)._terminate_contract(
                        wizard.terminate_reason_id,
                        wizard.terminate_comment,
                        wizard.terminate_date,
                    )
                else:
                    wizard.contract_id.with_context(is_cancel=True)._terminate_contract(
                        wizard.terminate_reason_id,
                        wizard.terminate_comment,
                        wizard.terminate_date,
                    )
            else:
                wizard.contract_id._terminate_contract(
                    wizard.terminate_reason_id,
                    wizard.terminate_comment,
                    wizard.terminate_date,
                )
        return True
