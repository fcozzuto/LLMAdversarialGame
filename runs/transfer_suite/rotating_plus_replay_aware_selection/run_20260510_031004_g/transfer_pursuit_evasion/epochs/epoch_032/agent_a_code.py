def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "") or "").lower()
    evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or (("pursuer" not in role) and ("chaser" not in role))

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs_set:
            nx, ny = sx, sy  # engine will keep in place on invalid moves
        d = dist2(nx, ny, ox, oy)
        if evader:
            score = d
            score += 0.01 * (nx - ox) * (nx - sx) + 0.01 * (ny - oy) * (ny - sy)  # deterministic tie-break
            # prefer keeping away from edges only when distances tie
            score += 0.001 * (min(nx, w - 1 - nx) + min(ny, h - 1 - ny))
            better = (best_score is None) or (score > best_score)
        else:
            score = -d
            score += 0.01 * (ox - nx) * (sx - nx) + 0.01 * (oy - ny) * (sy - ny)
            score += -0.001 * (min(nx, w - 1 - nx) + min(ny, h - 1 - ny))
            better = (best_score is None) or (score > best_score)
        if better:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]