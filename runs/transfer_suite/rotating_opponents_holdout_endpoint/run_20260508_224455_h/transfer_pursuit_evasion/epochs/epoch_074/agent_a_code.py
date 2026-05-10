def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    pursuer = ("pursu" in role) or ("chase" in role) or ("capt" in role)
    evader = ("evad" in role) or ("escap" in role)
    if not pursuer:
        pursuer = not evader

    obs_set = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x", -1)), int(p.get("y", -1))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def near_obs_penalty(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if (nx, ny) in obs_set:
                    pen += 2
        return pen

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs_set:
            continue
        d = dist2(nx, ny)
        if pursuer:
            score = -d - 0.25 * near_obs_penalty(nx, ny) - 0.01 * (abs(nx - sx) + abs(ny - sy))
        else:
            corners = ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1))
            cc = max(dist2(cx, cy) for cx, cy in corners)
            score = d + 0.35 * near_obs_penalty(nx, ny) + 0.001 * cc - 0.01 * (abs(nx - sx) + abs(ny - sy))
        key = (score, -dx, -dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]