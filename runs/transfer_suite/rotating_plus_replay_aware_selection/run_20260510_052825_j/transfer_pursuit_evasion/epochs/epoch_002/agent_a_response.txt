def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obstacles}
    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    def is_pursuer(role):
        r = role.replace("-", "_")
        return ("purs" in r) or (r == "pursuer")

    def is_evader(role):
        r = role.replace("-", "_")
        return ("evad" in r) or (r == "evader")

    pursuer = is_pursuer(self_role) and not is_evader(self_role)
    if not pursuer and is_pursuer(opp_role):
        pursuer = False
    elif pursuer and not is_evader(self_role):
        pursuer = True
    else:
        pursuer = is_pursuer(self_role)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_score = None

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        d_ = dist2(nx, ny, ox, oy)
        if pursuer:
            score = -d_
            # small deterministic tie-breakers: align diagonally toward opponent, avoid getting "stuck" by obstacles nearby
            align = (1 if (dx != 0 and dy != 0) else 0)
            near_block = 0
            for adx, ady in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ax, ay = nx + adx, ny + ady
                if in_bounds(ax, ay) and (ax, ay) in obs:
                    near_block += 1
            score = score * 100 + align * 2 - near_block
        else:
            # evader: maximize distance from pursuer, also prefer moves toward farthest corner
            score = d_
            far_corner = 0
            corners = ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1))
            best_corner_d = -1
            for cx, cy in corners:
                cd = dist2(nx, ny, cx, cy)
                if cd > best_corner_d:
                    best_corner_d = cd
                    far_corner = 1
            near_block = 0
            for adx, ady in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ax, ay = nx + adx, ny + ady
                if in_bounds(ax, ay) and (ax, ay) in obs:
                    near_block += 1
            score = score * 100 + best_corner_d - near_block

        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [best[0], best[1]]