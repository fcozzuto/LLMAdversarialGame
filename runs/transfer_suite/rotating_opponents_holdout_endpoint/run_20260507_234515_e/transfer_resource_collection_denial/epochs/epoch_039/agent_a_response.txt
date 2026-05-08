def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cd(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - cx) + abs(ny - cy)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Target resources that we can reach earlier than the opponent, and discourage resources near opponent's sweep axis (y).
    best_r = None
    best_v = None
    for rx, ry in resources:
        self_d = cd((sx, sy), (rx, ry))
        opp_d = cd((ox, oy), (rx, ry))
        benefit = opp_d - self_d
        v = benefit - 0.3 * abs(ry - oy) - 0.05 * abs(rx - ox)
        if best_v is None or v > best_v or (v == best_v and (self_d < cd((sx, sy), best_r) if best_r else True)):
            best_v = v
            best_r = (rx, ry)

    tx, ty = best_r
    target_dx = 0 if tx == sx else (1 if tx > sx else -1)
    target_dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If direct move is legal, take it; otherwise choose legal move that minimizes distance to target with opponent-aware tie-break.
    cand = (target_dx, target_dy)
    if cand in legal:
        return [cand[0], cand[1]]

    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_self = cd((nx, ny), (tx, ty))
        d_opp = cd((ox, oy), (tx, ty))
        interim_v = (d_opp - d_self) - 0.3 * abs(ty - oy)
        if best is None or interim_v > best[0] or (interim_v == best[0] and d_self < best[1]):
            best = (interim_v, d_self, dx, dy)
    return [best[2], best[3]]