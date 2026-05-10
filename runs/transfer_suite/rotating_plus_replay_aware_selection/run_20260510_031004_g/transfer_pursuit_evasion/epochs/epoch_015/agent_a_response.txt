def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("hunter" in self_role)
    if "evader" in self_role:
        pursuer = False
    if (("pursuer" in opponent_role) or ("pursuit" in opponent_role) or ("hunter" in opponent_role)) and ("evader" not in self_role):
        pursuer = True

    if not (0 <= sx < w and 0 <= sy < h):
        sx, sy = 0, 0
    if not (0 <= ox < w and 0 <= oy < h):
        ox, oy = w - 1, h - 1

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Prefer staying away from obstacles/edges to keep options; and align with pursuit/evasion.
    def wall_penalty(x, y):
        d = min(x, y, (w - 1) - x, (h - 1) - y)
        return -2.0 * d  # center better (higher d -> more negative when added with sign below)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue
        man = abs(nx - ox) + abs(ny - oy)
        # Obstacle proximity: count blocked neighbors (wants fewer if pursuer, more if evader).
        blocked = 0
        for tx in (-1, 0, 1):
            for ty in (-1, 0, 1):
                if tx == 0 and ty == 0:
                    continue
                ax, ay = nx + tx, ny + ty
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obs_set:
                    blocked += 1
        align = (dx * (1 if ox > sx else (-1 if ox < sx else 0)) + dy * (1 if oy > sy else (-1 if oy < sy else 0)))
        edge = wall_penalty(nx, ny)
        if pursuer:
            score = -man - 0.5 * blocked + 0.1 * align + 0.01 * edge
        else:
            score = man + 0.35 * blocked - 0.1 * align + 0.01 * (-edge)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]