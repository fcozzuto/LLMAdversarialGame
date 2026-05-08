def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    turns_remaining = observation.get("turns_remaining", 0)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    resset = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                res.append((x, y))
                resset.add((x, y))
    if not res:
        return [0, 0]

    dirs = (-1, 0, 1)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    try:
        tr = int(turns_remaining)
    except:
        tr = 0
    urgency = 1.0 + (max(0, 64 - tr) / 64.0)

    def best_dist_from(pos):
        px, py = pos
        bd = 10**9
        for rx, ry in res:
            d = abs(px - rx) + abs(py - ry)
            if d < bd:
                bd = d
        return bd

    self_cur_bd = best_dist_from((sx, sy))
    opp_cur_bd = best_dist_from((ox, oy))

    best_move = [0, 0]
    best_val = -10**18

    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue

            self_next = (nx, ny)
            self_bd = best_dist_from(self_next)
            self_gain = (self_cur_bd - self_bd)

            # Opponent denial: estimate how much our move makes it harder for them to get close.
            # Compute opponent best achievable distance after one move.
            opp_best_next_bd = 10**9
            for odx in dirs:
                for ody in dirs:
                    tx, ty = ox + odx, oy + ody
                    if inb(tx, ty):
                        d = best_dist_from((tx, ty))
                        if d < opp_best_next_bd:
                            opp_best_next_bd = d

            opp_gain = (opp_cur_bd - opp_best_next_bd)

            # Immediate capture bonus if we land on a resource cell.
            capture = 1.0 if (nx, ny) in resset else 0.0

            # Prefer moves that reduce distance more strongly when time is low.
            val = (capture * 1000.0 + urgency * (self_gain * 3.0) - (urgency * 0.9) * (opp_gain * 2.0))

            # Small tie-break toward staying aligned with opponent to discourage interception.
            val += -0.01 * (man(self_next, (ox, oy)) if self_next else 0)

            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move