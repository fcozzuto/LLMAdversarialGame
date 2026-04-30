def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = (0, 0)
    best_val = -10**18

    # Bias toward breaking symmetry late: prefer moves that reduce our distance to the opponent's nearest "threat" resource.
    # Also prefer resources where we are not strictly behind the opponent.
    # No random tie-breaking: use fixed order and keep first best.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Safety penalty: don't move into immediate contact if it would make us obviously worse.
        opp_adj = cheb(nx, ny, ox, oy)
        safety = 0
        if opp_adj <= 1:
            safety -= 0.5 * opp_adj

        # Find our closest and opponent's closest resource to determine focus.
        our_best_d = 10**9
        opp_best_d = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            if our_d < our_best_d:
                our_best_d = our_d
            if opp_d < opp_best_d:
                opp_best_d = opp_d
        if our_best_d == 10**9:
            continue

        # Main value: maximize "reach advantage" over opponent across resources, but emphasize those we can realistically secure.
        val = 0.0
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            du = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we are closer or tied, high reward; if behind, still some reward if we improve enough.
            reach_adv = do - du  # positive is good
            # Strongly reward near-term capture.
            near_bonus = 0
            if du == 0:
                near_bonus = 1000
            elif du == 1:
                near_bonus = 40
            elif du == 2:
                near_bonus = 12
            # Penalize being behind, especially when opponent is very close.
            behind_pen = 0
            if reach_adv < 0:
                behind_pen = (-reach_adv) * (8 + 2 * min(do, 3))
            # Slight preference for resources that are "contested" (both distances similar).
            contested = -0.2 * abs(du - do)
            val += (reach_adv * 9) + near_bonus + contested - behind_pen

        # Additional focus: if opponent has a very close resource, prioritize denying it by reducing our distance to that region.
        threat_focus = 0
        min_opp_resource = None
        min_opp_d = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            od = cheb(ox, oy, rx, ry)
            if od < min_opp_d:
                min_opp_d = od
                min_opp_resource = (rx, ry)
        if min_opp_resource is not None:
            trx, try_ = min_opp_resource
            du_threat = cheb(nx, ny, trx, try_)
            # If opponent is close, deny it by reducing our distance too.
            if min_opp_d <= 2:
                threat_focus = (min_opp_d - du_threat) * 6

        val += safety + threat_focus

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]