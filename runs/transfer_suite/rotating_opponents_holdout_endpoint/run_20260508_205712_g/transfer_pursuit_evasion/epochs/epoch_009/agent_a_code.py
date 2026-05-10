def choose_move(observation):
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

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

    evader = self_ev or (not self_pu and opp_pu) or (opp_ev and not self_pu)
    pursuer = self_pu or (not self_ev and opp_ev) or (opp_pu and not self_ev)
    if not evader and not pursuer:
        pursuer = True

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_move(nx, ny):
        if not in_bounds(nx, ny):
            return -10**9 if pursuer else -10**8
        if (nx, ny) in obs:
            return -10**8 if pursuer else -10**7
        d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if pursuer:
            # Prefer closing distance; also prefer avoiding obstacles locally.
            best_obs = 0
            for ax, ay in obs_list:
                pass
            # fixed small local penalty
            pen = 0
            for ax, ay in obs:
                md = abs(nx - ax) + abs(ny - ay)
                if md == 0:
                    pen += 1000
                elif md == 1:
                    pen += 20
                elif md == 2:
                    pen += 6
            return d * (-1) - pen * 1.0 + (-0.01) * (abs(nx - sx) + abs(ny - sy))
        else:
            # Prefer maximizing distance; bias toward corners opposite opponent for corner-evasion.
            pen = 0
            for ax, ay in obs:
                md = abs(nx - ax) + abs(ny - ay)
                if md == 0:
                    pen += 1000
                elif md == 1:
                    pen += 20
                elif md == 2:
                    pen += 6
            # Corner target: farthest corner from opponent, then keep moving there.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            tx, ty = corners[0]
            best = -1
            for cx, cy in corners:
                cd = abs(cx - ox) + abs(cy - oy)
                if cd > best:
                    best = cd
                    tx, ty = cx, cy
            corner_bias = -(abs(nx - tx) + abs(ny - ty))
            return d + corner_bias * 1.2 - pen * 1.0 - 0.01 * (abs(nx - sx) + abs(ny - sy))

    # Deterministic tie-breaking: iterate deltas in fixed order.
    best_val = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        v = score_move(nx, ny)
        if best_val is None or (pursuer and v > best_val) or ((not pursuer) and v > best_val):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]