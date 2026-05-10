def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_list = observation.get("obstacles", []) or []
    obs = set()
    for a in obs_list:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))

    def role_flags(r):
        r = str(r or "").lower()
        ev = ("evad" in r) or ("run" in r) or ("esc" in r)
        pu = ("purs" in r) or ("catch" in r) or ("pred" in r) or ("hunt" in r)
        return ev, pu

    self_ev, self_pu = role_flags(observation.get("self_role", ""))
    opp_ev, opp_pu = role_flags(observation.get("opponent_role", ""))
    evader = self_ev or (not self_pu and opp_pu) or (opp_ev and not self_ev and self_pu is False)
    pursuer = self_pu or (not self_ev and opp_ev) or (opp_pu and not self_pu)

    if not evader and not pursuer:
        pursuer = True

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obst_pen(nx, ny):
        if not obs:
            return 0
        best = 999
        for ax, ay in obs:
            d = abs(nx - ax) + abs(ny - ay)
            if d < best:
                best = d
        # Larger when close to obstacles; discourage proximity for stability
        return 10.0 / (1.0 + best)

    # Corner bias (deterministic): for evader go to farthest corner, for pursuer go to nearest corner
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if evader:
        far_corner = max(corners, key=lambda c: manhattan(c[0], c[1], ox, oy))
    else:
        far_corner = min(corners, key=lambda c: manhattan(c[0], c[1], ox, oy))

    best_move = (0, 0)
    best_score = -10**18 if pursuer else 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d_to_op = manhattan(nx, ny, ox, oy)
        d_to_corner = manhattan(nx, ny, far_corner[0], far_corner[1])
        op_corner = manhattan(ox, oy, far_corner[0], far_corner[1])

        # pursuer: minimize opponent distance; also nudge toward corner where opponent is
        # evader: maximize opponent distance; also push toward far corner and away from obstacles
        o_pen = obst_pen(nx, ny)
        if pursuer:
            score = (-d_to_op) + (0.03 * (op_corner - d_to_corner)) - (0.35 * o_pen)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            score = (d_to_op) + (0.02 * d_to_corner) - (0.45 * o_pen)
            if score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]