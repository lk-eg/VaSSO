import torch
import torch.optim

from utils.configurable import configurable
from solver.build import OPTIMIZER_REGISTRY

from solver.vassore import VASSORE


@OPTIMIZER_REGISTRY.register()
class VASSOREMU(VASSORE):
    @configurable()
    def __init__(
        self,
        params,
        base_optimizer,
        logger,
        rho,
        theta,
        max_epochs,
        extensive_metrics_mode,
        performance_scores_mode,
        crt,
        crt_k,
        crt_p,
        crt_z,
        z_two,
        lam,
        crt_c,
        var_delta,
    ) -> None:
        super().__init__(
            params,
            base_optimizer,
            logger,
            rho,
            theta,
            max_epochs,
            extensive_metrics_mode,
            performance_scores_mode,
            crt,
            crt_k,
            crt_p,
            crt_z,
            z_two,
            lam,
            crt_c,
            var_delta,
        )

    @torch.no_grad()
    def first_step(self, zero_grad=False):
        self._ema_update()
        self._perturbation(zero_grad)

    """
    HELPER methods overrides
    """

    def _ema_update_inner(self, p, theta):
        self.state[p]["ema"].mul_(1 - theta)
        gradient = torch.zeros_like(p).to(p)
        if self.inner_gradient_calculation(self):
            gradient = p.grad
        else:
            gradient = self.state[p]["g_t"]
        self.state[p]["ema"].add_(gradient, alpha=theta)
