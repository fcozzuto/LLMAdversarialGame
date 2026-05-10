def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()

    def is_ev(r):
        r = (r or "").replace("-", "_")
        return ("evad" in r) or (r == "evader")

    def is_pu(r):
        r = (r or "").replace("-", "_")
        return ("purs" in r) or (r == "pursuer")

    if is_pu(self_role) and not is_ev(self_role):
        pursuer = True
    elif is_pu(opponent_role) and not is_ev(opponent_role):
        pursuer = False
    else:
        pursuer = True

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def d2(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx * dx + dy * dy

    best_dx, best_dy = 0, 0
    best_val = -10**18 if pursuer else 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        dist_sq = d2(nx, ny, ox, oy)
        corner_dist = max(d2(nx, ny, cx, cy) for (cx, cy) in corners)
        # obstacle proximity penalty/bonus
        near_obs = 0
        for (bx, by) in obs:
            dd = abs(nx - bx) + abs(ny - by)
            if dd == 0:
                near_obs += 1000
            elif dd == 1:
                near_obs += 5
            elif dd == 2:
                near_obs += 1

        # Deterministic tie-break: prefer moves earlier in deltas ordering
        if pursuer:
            val = -dist_sq + 0.01 * corner_dist - 0.5 * near_obs
            if (dist_sq == 0) or (val > best_val + 1e-12):
                best_val = val
                best_dx, best_dy = dx, dy
        else:
            val = dist_sq + 0.01 * corner_dist - 0.5 * near_obs
            if (dist_sq > 0 and val > best_val + 1e-12) or (dist_sq == 0 and best_val == 10**18):
                best_val = val
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]