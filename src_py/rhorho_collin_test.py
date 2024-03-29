
import numpy as np
from src_py.particle import Particle
from src_py.math_utils import *


class RhoRhoEvent(object):
    def __init__(self, data, args, debug=True):
        # [n, pi-, pi0, an, pi+, pi0]
        # 5 * i + 1
        # np.save('demo_data',data)
        p = [Particle(data[:, 5 * i:5 * i + 4]) for i in range(6)]
        cols = []
        labels = []
        self.labels_suppl = []
        self.cols_suppl = []

        def get_tau1(p):
            tau1_nu  = p[0]
            tau1_pi  = p[1:3]
            tau1_rho = tau1_pi[0] + tau1_pi[1]
            tau1     = tau1_rho+tau1_nu

            return tau1_nu, tau1_pi, tau1_rho, tau1

        def get_tau2(p):
            tau2_nu = p[3]
            tau2_pi = p[4:6]
            tau2_rho = tau2_pi[0] + tau2_pi[1]
            tau2 = tau2_rho+tau2_nu

            return tau2_nu, tau2_pi, tau2_rho, tau2

        p_tau1_nu, l_tau1_pi, p_tau1_rho,  p_tau1 = get_tau1(p) # p- particle, l-list
        p_tau2_nu, l_tau2_pi, p_tau2_rho,  p_tau2 = get_tau2(p)

        rho1_theta = p_tau1_rho.angle_theta
        nu1_theta = p_tau1_nu.angle_theta
        rho1_phi = p_tau1_rho.angle_phi
        nu1_phi = p_tau1_nu.angle_phi
        rho2_theta = p_tau2_rho.angle_theta
        nu2_theta = p_tau2_nu.angle_theta
        rho2_phi = p_tau2_rho.angle_phi
        nu2_phi = p_tau2_nu.angle_phi

        theta_err1 = rho1_theta/nu1_theta - 1
        phi_err1 = rho1_phi/nu1_phi - 1
        theta_err2 = rho2_theta/nu2_theta - 1
        phi_err2 = rho2_phi/nu2_phi - 1

        self.rho_nu_theta_err = [theta_err1, theta_err2]
        self.rho_nu_phi_err = [phi_err1, phi_err2]

        rho_rho = p_tau1_rho + p_tau2_rho

        PHI, THETA = calc_angles(p_tau1_rho, rho_rho)
        beta_noise = args.BETA

        if args.FEAT == "Collin-approx":
            nu1 = p[0]
            nu2 = p[3]
            e_miss_x = nu1.vec[:,0] + nu2.vec[:,0]
            e_miss_y = nu1.vec[:,1] + nu2.vec[:,1]
            p_vis_x1 = p_tau1_rho.vec[:,0]
            p_vis_y1 = p_tau1_rho.vec[:,1]
            p_vis_x2 = p_tau2_rho.vec[:,0]
            p_vis_y2 = p_tau2_rho.vec[:,1]

            a2 = (e_miss_y*p_vis_x1 - e_miss_x*p_vis_y1)/(p_vis_y2*p_vis_x1 - p_vis_x2*p_vis_y1)
            a1 = (e_miss_x - a2*p_vis_x2)/p_vis_x1

            if a1 < 0 or a2 < 0:
                a1 = 0
                a2 = 0

            nu_approx = [Particle(a1[:,None]*(p_tau1_rho.vec)), Particle(a2[:,None]*(p_tau2_rho.vec))]

        # all particles boosted & rotated
        for i, idx in enumerate([0, 1, 2, 3, 4, 5]):
            part = boost_and_rotate(p[idx], PHI, THETA, rho_rho)
            if args.FEAT in ["Variant-1.0", "Variant-1.1", "Variant-2.0", "Variant-2.1", "Variant-2.2",
                             "Variant-3.0", "Variant-3.1", "Variant-4.0", "Variant-4.1"]:
                if idx not in [0, 3]:
                    cols.append(part.vec)
            if args.FEAT == "Variant-All":
                cols.append(part.vec)
            if args.FEAT == "Collin-approx":
                if idx not in [0, 3]:
                    cols.append(part.vec)
                elif idx == 0:
                    part = boost_and_rotate(nu_approx[0], PHI, THETA, rho_rho)
                    cols.append(part.vec)
                elif idx == 3:
                    part = boost_and_rotate(nu_approx[1], PHI, THETA, rho_rho)
                    cols.append(part.vec)
                
        if args.FEAT == "Collin-approx":
            np.save(args.IN + "/approx_cols.npy", cols)
        if args.FEAT == "Variant-All":
            np.save(args.IN + "/ori_cols.npy", cols)

        if args.FEAT == "Variant-4.0":
            part   = boost_and_rotate(p_tau1, PHI, THETA, rho_rho)
            cols.append(part.vec)
            part   = boost_and_rotate(p_tau2, PHI, THETA, rho_rho)
            cols.append(part.vec)
            

        if args.FEAT == "Variant-4.1":
            p_tau1_approx = scale_lifetime(p_tau1)
            part   = boost_and_rotate(p_tau1_approx, PHI, THETA, rho_rho)
            cols.append(part.vec)
            p_tau2_approx = scale_lifetime(p_tau2)
            part   = boost_and_rotate(p_tau2_approx, PHI, THETA, rho_rho)
            cols.append(part.vec)
            self.cols_suppl.append(p_tau1_approx.x/p_tau1.x)
            self.cols_suppl.append(p_tau1_approx.y/p_tau1.y)
            self.cols_suppl.append(p_tau1_approx.z/p_tau1.z)
            self.cols_suppl.append(p_tau1_approx.e/p_tau1.e)
            self.cols_suppl.append(p_tau2_approx.x/p_tau2.x)
            self.cols_suppl.append(p_tau2_approx.y/p_tau2.y)
            self.cols_suppl.append(p_tau2_approx.z/p_tau2.z)
            self.cols_suppl.append(p_tau2_approx.e/p_tau2.e)
            self.cols_suppl.append(p_tau1.vec)
            self.cols_suppl.append(p_tau2.vec)
            self.cols_suppl.append(p_tau1.pt)
            self.cols_suppl.append(p_tau2.pt)
            self.cols_suppl.append(l_tau1_pi[0].pt)
            self.cols_suppl.append(l_tau2_pi[0].pt)
 
        # rho particles & recalculated mass 
        if args.FEAT == "Variant-1.1":
            for i, rho in enumerate([p_tau1_rho] + [p_tau2_rho]):
                rho = boost_and_rotate(rho, PHI, THETA, rho_rho)
                cols.append(rho.vec)
                cols.append(rho.recalculated_mass)

        if args.FEAT == "Variant-1.1":
            cols += [get_acoplanar_angle(p[1], p[2], p[4], p[5], rho_rho)]
            cols += [get_y(p[1], p[2], rho_rho), get_y(p[4], p[5], rho_rho)]

        #------------------------------------------------------------

        pb_tau1_h  = boost_and_rotate(p_tau1_rho, PHI, THETA, rho_rho)
        pb_tau2_h  = boost_and_rotate(p_tau2_rho, PHI, THETA, rho_rho)
        pb_tau1_nu = boost_and_rotate(p_tau1_nu, PHI, THETA, rho_rho)
        pb_tau2_nu = boost_and_rotate(p_tau2_nu, PHI, THETA, rho_rho)

        #------------------------------------------------------------

        v_ETmiss_x = p_tau1_nu.x + p_tau2_nu.x
        v_ETmiss_y = p_tau1_nu.y + p_tau2_nu.y
        
        if args.FEAT == "Variant-2.2":
            cols += [v_ETmiss_x, v_ETmiss_y]

        #------------------------------------------------------------

        if args.METHOD == "A":
            va_alpha1, va_alpha2 = approx_alpha_A(v_ETmiss_x, v_ETmiss_y, p_tau1_rho, p_tau2_rho)
        elif args.METHOD == "B":
            va_alpha1, va_alpha2 = approx_alpha_B(v_ETmiss_x, v_ETmiss_y, p_tau1_rho, p_tau2_rho)
        elif args.METHOD == "C":
            va_alpha1, va_alpha2 = approx_alpha_C(v_ETmiss_x, v_ETmiss_y, p_tau1_rho, p_tau2_rho)

        #------------------------------------------------------------

        va_tau1_nu_long = va_alpha1 * pb_tau1_h.z
        va_tau2_nu_long = va_alpha2 * pb_tau2_h.z

        va_tau1_nu_E = approx_E_nu(pb_tau1_h, va_tau1_nu_long)
        va_tau2_nu_E = approx_E_nu(pb_tau2_h, va_tau2_nu_long)

        #------------------------------------------------------------

        va_tau1_nu_trans = np.sqrt(np.square(va_tau1_nu_E) - np.square(va_tau1_nu_long))
        va_tau2_nu_trans = np.sqrt(np.square(va_tau2_nu_E) - np.square(va_tau2_nu_long))
 
        v_tau1_nu_phi    = np.arctan2(pb_tau1_nu.x, pb_tau1_nu.y) #boosted
        v_tau2_nu_phi    = np.arctan2(pb_tau2_nu.x, pb_tau2_nu.y)
        vn_tau1_nu_phi   = smear_exp(v_tau1_nu_phi, beta_noise)
        vn_tau2_nu_phi   = smear_exp(v_tau2_nu_phi, beta_noise)

        tau1_sin_phi = np.sin(vn_tau1_nu_phi)
        tau1_cos_phi = np.cos(vn_tau1_nu_phi)
        tau2_sin_phi = np.sin(vn_tau2_nu_phi)
        tau2_cos_phi = np.cos(vn_tau2_nu_phi)

        #------------------------------------------------------------

        ve_x1_cms = pb_tau1_h.z / (pb_tau1_h + pb_tau1_nu).z
        ve_x2_cms = pb_tau2_h.z / (pb_tau2_h + pb_tau2_nu).z

        ve_alpha1_cms = 1/ve_x1_cms - 1
        ve_alpha2_cms = 1/ve_x2_cms - 1

        ve_tau1_nu_long = ve_alpha1_cms * pb_tau1_h.z
        ve_tau2_nu_long = ve_alpha2_cms * pb_tau2_h.z

        ve_tau1_nu_E = approx_E_nu(pb_tau1_h, ve_tau1_nu_long)
        ve_tau2_nu_E = approx_E_nu(pb_tau2_h, ve_tau2_nu_long)

        ve_tau1_nu_trans = np.sqrt(np.square(ve_tau1_nu_E) - np.square(ve_tau1_nu_long))
        ve_tau2_nu_trans = np.sqrt(np.square(ve_tau2_nu_E) - np.square(ve_tau2_nu_long))


        if args.FEAT in ["Variant-2.1", "Variant-2.2"]:
            cols += [va_tau1_nu_long, va_tau2_nu_long, va_tau1_nu_E, va_tau2_nu_E, va_tau1_nu_trans, va_tau2_nu_trans]

        elif args.FEAT in ["Variant-3.0", "Variant-3.1"]:
            cols += [va_tau1_nu_long, va_tau2_nu_long, va_tau1_nu_E, va_tau2_nu_E, va_tau1_nu_trans * tau1_sin_phi,
                     va_tau2_nu_trans * tau2_sin_phi, va_tau1_nu_trans * tau1_cos_phi, va_tau2_nu_trans * tau2_cos_phi]

        elif args.FEAT == "Variant-2.0":
            cols += [ve_tau1_nu_long, ve_tau2_nu_long, ve_tau1_nu_E, ve_tau2_nu_E, ve_tau1_nu_trans, ve_tau2_nu_trans]

        # filter
        filt = (p_tau1_rho.pt >= 20) & (p_tau2_rho.pt >= 20)
        for part in (l_tau1_pi + l_tau2_pi):
            filt = filt & (part.pt >= 1)
        filt = filt.astype(np.float32)

        if args.FEAT in ["Variant-1.0", "Variant-1.1", "Variant-All", "Variant-4.0", "Variant-4.1", "Collin-approx"]:
            cols += [filt]
 
        elif args.FEAT in ["Variant-2.1", "Variant-2.2", "Variant-3.0", "Variant-3.1"]:
            isFilter = np.full(rho_rho.e.shape, True, dtype=bool)

            va_alpha1_A, va_alpha2_A = approx_alpha_A(v_ETmiss_x, v_ETmiss_y, p_tau1_rho, p_tau2_rho)
            va_alpha1_B, va_alpha2_B = approx_alpha_B(v_ETmiss_x, v_ETmiss_y, p_tau1_rho, p_tau2_rho)
            va_alpha1_C, va_alpha2_C = approx_alpha_C(v_ETmiss_x, v_ETmiss_y, p_tau1_rho, p_tau2_rho)

            va_tau1_nu_long_A = va_alpha1_A * pb_tau1_h.z
            va_tau1_nu_long_B = va_alpha1_B * pb_tau1_h.z 
            va_tau1_nu_long_C = va_alpha1_C * pb_tau1_h.z

            va_tau2_nu_long_A = va_alpha2_A * pb_tau2_h.z
            va_tau2_nu_long_B = va_alpha2_B * pb_tau2_h.z 
            va_tau2_nu_long_C = va_alpha2_C * pb_tau2_h.z
		
            va_tau1_nu_E_A = approx_E_nu(pb_tau1_h, va_tau1_nu_long_A)
            va_tau1_nu_E_B = approx_E_nu(pb_tau1_h, va_tau1_nu_long_B)
            va_tau1_nu_E_C = approx_E_nu(pb_tau1_h, va_tau1_nu_long_C)

            va_tau2_nu_E_A = approx_E_nu(pb_tau2_h, va_tau2_nu_long_A)
            va_tau2_nu_E_B = approx_E_nu(pb_tau2_h, va_tau2_nu_long_B)
            va_tau2_nu_E_C = approx_E_nu(pb_tau2_h, va_tau2_nu_long_C)

            va_tau1_nu_trans_A = np.sqrt(np.square(va_tau1_nu_E_A) - np.square(va_tau1_nu_long_A))
            va_tau1_nu_trans_B = np.sqrt(np.square(va_tau1_nu_E_B) - np.square(va_tau1_nu_long_B))
            va_tau1_nu_trans_C = np.sqrt(np.square(va_tau1_nu_E_C) - np.square(va_tau1_nu_long_C))

            va_tau2_nu_trans_A = np.sqrt(np.square(va_tau2_nu_E_A) - np.square(va_tau2_nu_long_A))
            va_tau2_nu_trans_B = np.sqrt(np.square(va_tau2_nu_E_B) - np.square(va_tau2_nu_long_B))
            va_tau2_nu_trans_C = np.sqrt(np.square(va_tau2_nu_E_C) - np.square(va_tau2_nu_long_C))
                  

            for alpha in [va_alpha1_A, va_alpha1_B, va_alpha1_C, va_alpha2_A, va_alpha2_B, va_alpha2_C]:
                isFilter *= (alpha > 0)
            for energy in [va_tau1_nu_E_A, va_tau1_nu_E_B, va_tau1_nu_E_C, va_tau2_nu_E_A, va_tau2_nu_E_B, va_tau2_nu_E_C]:
                isFilter *= (energy > 0)
            for trans_comp in [va_tau1_nu_trans_A, va_tau1_nu_trans_B, va_tau1_nu_trans_C, va_tau2_nu_trans_A, va_tau2_nu_trans_B, va_tau2_nu_trans_C]:
                isFilter *= np.logical_not(np.isnan(trans_comp))
            cols += [filt * isFilter]

        elif args.FEAT in ["Variant-2.0"]:
            isFilter = np.full(rho_rho.e.shape, True, dtype=bool)
            for alpha in [ve_alpha1_cms, ve_alpha2_cms]:
                isFilter *= (alpha > 0)
            for energy in [ve_tau1_nu_E, ve_tau2_nu_E]:
                isFilter *= (energy > 0)
            for trans_comp in [ve_tau1_nu_trans, ve_tau2_nu_trans]:
                isFilter *= np.logical_not(np.isnan(trans_comp))
            cols += [filt * isFilter]


        for i in range(len(cols)):
            if len(cols[i].shape) == 1:
                cols[i] = cols[i].reshape([-1, 1])
        for i in range(len(self.cols_suppl)):
            if len(self.cols_suppl[i].shape) == 1:
                self.cols_suppl[i] = self.cols_suppl[i].reshape([-1, 1])
             
        self.cols = np.concatenate(cols, 1)
        if len(self.cols_suppl) >0 :
            self.cols_suppl = np.concatenate(self.cols_suppl, 1)

        # this part is for smeared in Variant-3.1
        if args.BETA > 0:
            vn_tau1_nu_phi = smear_polynomial(v_tau1_nu_phi, args.BETA, args.pol_b, args.pol_c)
            vn_tau2_nu_phi = smear_polynomial(v_tau2_nu_phi, args.BETA, args.pol_b, args.pol_c)

            tau1_sin_phi = np.sin(vn_tau1_nu_phi)
            tau1_cos_phi = np.cos(vn_tau1_nu_phi)
            tau2_sin_phi = np.sin(vn_tau2_nu_phi)
            tau2_cos_phi = np.cos(vn_tau2_nu_phi)
        self.valid_cols = [va_tau1_nu_trans * tau1_sin_phi, va_tau2_nu_trans * tau2_sin_phi,
                           va_tau1_nu_trans * tau1_cos_phi, va_tau2_nu_trans * tau2_cos_phi]

        # now comes the list of labels for monitoring feautures

        if args.FEAT == "Variant-1.1":
            self.labels = ["tau1_pi_px", "tau1_pi_py", "tau1_pi_pz", "tau1_pi_e", "tau1_pi0_px", "tau1_pi0_py", "tau1_pi0_pz", "tau1_pi0_e",
                           "tau2_pi_px", "tau2_pi_py", "tau2_pi_pz", "tau2_pi_e", "tau2_pi0_px", "tau2_pi0_py", "tau2_pi0_pz", "tau2_pi0_e",
                           "tau1_rho_px", "tau1_rho_py", "tau1_rho_pz", "tau1_rho_e", "tau1_rho_mass",
                           "tau2_rho_px", "tau2_rho_py", "tau2_rho_pz", "tau2_rho_e", "tau2_rho_mass",
                           "aco_angle", "tau1_y", "tau2_y"]

        elif args.FEAT ==  "Variant-2.0":
            self.labels = ["tau1_pi_px", "tau1_pi_py", "tau1_pi_pz", "tau1_pi_e", "tau1_pi0_px", "tau1_pi0_py", "tau1_pi0_pz", "tau1_pi0_e",
                           "tau2_pi_px", "tau2_pi_py", "tau2_pi_pz", "tau2_pi_e", "tau2_pi0_px", "tau2_pi0_py", "tau2_pi0_pz", "tau2_pi0_e",
                           "tau1_nu_pL", "tau2_nu_pL", "tau1_nu_e", "tau2_nu_e", "tau1_nu_pT", "tau2_nu_pT"]
        elif args.FEAT ==  "Variant-2.1":
            self.labels = ["tau1_pi_px", "tau1_pi_py", "tau1_pi_pz", "tau1_pi_e", "tau1_pi0_px", "tau1_pi0_py", "tau1_pi0_pz", "tau1_pi0_e",
                           "tau2_pi_px", "tau2_pi_py", "tau2_pi_pz", "tau2_pi_e", "tau2_pi0_px", "tau2_pi0_py", "tau2_pi0_pz", "tau2_pi0_e",
                           "tau1_nu_approx_pL", "tau2_nu_approx_pL", "tau1_nu_approx_e", "tau2_nu_approx_e", "tau1_nu_approx_pT", "tau2_nu_approx_pT"]
        elif args.FEAT ==  "Variant-2.2":
            self.labels = [ "tau1_pi_px", "tau1_pi_py", "tau1_pi_pz", "tau1_pi_e", "tau1_pi0_px", "tau1_pi0_py", "tau1_pi0_pz", "tau1_pi0_e",
                            "tau2_pi_px", "tau2_pi_py", "tau2_pi_pz", "tau2_pi_e", "tau2_pi0_px", "tau2_pi0_py", "tau2_pi0_pz", "tau2_pi0_e",
                            "ETmiss_px", "ETmiss_py",
                            "tau1_nu_approx_pL", "tau2_nu_approx_pL", "tau1_nu_approx_e", "tau2_nu_approx_e", "tau1_nu_approx_pT", "tau2_nu_approx_pT"]

        elif args.FEAT ==  "Variant-3.0":
            self.labels = ["tau1_pi_px", "tau1_pi_py", "tau1_pi_pz", "tau1_pi_e", "tau1_pi0_px", "tau1_pi0_py", "tau1_pi0_pz", "tau1_pi0_e",
                           "tau2_pi_px", "tau2_pi_py", "tau2_pi_pz", "tau2_pi_e", "tau2_pi0_px", "tau2_pi0_py", "tau2_pi0_pz", "tau2_pi0_e",
                           "tau1_nu_approx_px", "tau1_nu_approx_py", "tau2_nu_approx_px", "tau1_nu_approx_py"]
        elif args.FEAT ==  "Variant-3.1":
            self.labels = ["tau1_pi_px", "tau1_pi_py", "tau1_pi_pz", "tau1_pi_e", "tau1_pi0_px", "tau1_pi0_py", "tau1_pi0_pz", "tau1_pi0_e",
                           "tau2_pi_px", "tau2_pi_py", "tau2_pi_pz", "tau2_pi_e", "tau2_pi0_px", "tau2_pi0_py", "tau2_pi0_pz", "tau2_pi0_e",
                           "tau1_nu_approx_px", "tau1_nu_approx_py", "tau2_nu_approx_px", "tau1_nu_approx_py"]

        elif args.FEAT ==  "Variant-4.0":
            self.labels = ["tau1_pi_px", "tau1_pi_py", "tau1_pi_pz", "tau1_pi_e", "tau1_pi0_px", "tau1_pi0_py", "tau1_pi0_pz", "tau1_pi0_e",
                           "tau2_pi_px", "tau2_pi_py", "tau2_pi_pz", "tau2_pi_e", "tau2_pi0_px", "tau2_pi0_py", "tau2_pi0_pz", "tau2_pi0_e",
                           "tau1_px", "tau1_py", "tau1_pz", "tau1_e", "tau2_px", "tau2_py", "tau2_pz", "tau2_e"]
        elif args.FEAT ==  "Variant-4.1":
            self.labels = ["tau1_pi_px", "tau1_pi_py", "tau1_pi_pz", "tau1_pi_e", "tau1_pi0_px", "tau1_pi0_py", "tau1_pi0_pz", "tau1_pi0_e",
                           "tau2_pi_px", "tau2_pi_py", "tau2_pi_pz", "tau2_pi_e", "tau2_pi0_px", "tau2_pi0_py", "tau2_pi0_pz", "tau2_pi0_e",
                           "tau1_approx_px", "tau1_approx_py", "tau1_approx_pz", "tau1_approx_e",
                           "tau2_approx_px", "tau2_approx_py", "tau2_approx_pz", "tau2_approx_e"]
            self.labels_suppl = ["tau1_px_ratio_LAB","tau1_py_ratio_LAB","tau1_pz_ratio_LAB","tau1_e_ratio_LAB",
                                 "tau2_px_ratio_LAB","tau2_py_ratio_LAB","tau2_pz_ratio_LAB","tau2_e_ratio_LAB",
                                 "tau1_px_LAB", "tau1_py_LAB", "tau1_pz_LAB", "tau1_e_LAB",
                                 "tau2_px_LAB", "tau2_py_LAB", "tau2_pz_LAB", "tau2_e_LAB",
                                  "tau1_pT_LAB", "tau2_pT_LAB", "tau1_pi_pT_LAB", "tau2_pi_pT_LAB"]

        elif args.FEAT == "Variant-All":
            self.labels = ["tau1_nu_px", "tau1_nu_py", "tau1_nu_pz", "tau1_nu_e",
                           "tau1_pi_px", "tau1_pi_py", "tau1_pi_pz", "tau1_pi_e", "tau1_pi0_px", "tau1_pi0_py", "tau1_pi0_pz", "tau1_pi0_e",
                           "tau2_nu_px", "tau2_nu_py", "tau2_nu_pz", "tau2_nu_e",
                           "tau2_pi_px", "tau2_pi_py", "tau2_pi_pz", "tau2_pi_e", "tau2_pi0_px", "tau2_pi0_py", "tau2_pi0_pz", "tau2_pi0_e"]

        elif args.FEAT == "Variant-1.0":
                self.labels = ["tau1_pi_px", "tau1_pi_py", "tau1_pi_pz", "tau1_pi_e", "tau1_pi0_px", "tau1_pi0_py",
                               "tau1_pi0_pz", "tau1_pi0_e",
                               "tau2_pi_px", "tau2_pi_py", "tau2_pi_pz", "tau2_pi_e", "tau2_pi0_px", "tau2_pi0_py",
                               "tau2_pi0_pz", "tau2_pi0_e"]

