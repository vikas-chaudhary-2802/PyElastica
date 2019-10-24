__doc__ = """ Interaction module """

import numpy as np

from ._linalg import _batch_matmul, _batch_matvec, _batch_cross


class InteractionPlane:
    def __init__(self, k, nu, origin_plane, normal_plane):
        self.k = k
        self.nu = nu
        self.origin_plane = origin_plane
        self.normal_plane = normal_plane
        self.surface_tol = 1e-4

    def apply_force(self, rod):
        element_x = 0.5 * (rod.x[..., :-1] + rod.x[..., 1:])
        distance_from_plane = self.normal_plane @ (element_x - self.origin_plane)
        contact_pts = np.where(distance_from_plane < self.surface_tol)
        total_forces = (rod.internal_forces[..., contact_pts]
                        + rod.external_forces[..., contact_pts])
        forces_normal_direction = self.normal_plane @ total_forces
        forces_normal = np.outer(self.normal_plane, forces_normal_direction)
        forces_normal[..., np.where(forces_normal_direction > 0)] = 0
        plane_penetration = (np.minimum(distance_from_plane[contact_pts]
                             - rod.r[contact_pts], 0.0))
        elastic_force = -self.k * np.outer(self.normal_plane,
                                           plane_penetration)
        normal_v = self.normal_plane @ rod.v[..., contact_pts]
        damping_force = -self.nu * np.outer(self.normal_plane, normal_v)
        normal_force_plane = -forces_normal
        total_force_plane = normal_force_plane + elastic_force + damping_force
        rod.external_forces[..., contact_pts] += 0.5 * total_force_plane
        rod.external_forces[..., contact_pts + 1] += 0.5 * total_force_plane