def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = False
    if self_role:
        pursuer = ("evad" not in self_role) and ("purs" in self_role or "hunter" in self_role or "pursuer" in self_role or "chaser" in self_role or "pursuer" == self_role)
        if not ("purs" in self_role or "hunter" in self_role or "pursuer" in self_role or "chaser" in self_role or "evad" in self_role):
            pursuer = True
    elif opponent_role:
        pursuer = ("evad" not in opponent_role)
    else:
        pursuer = True

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d = abs(nx - ox) + abs(ny - oy)
        score = (-d if pursuer else d, -abs(dx) - abs(dy))
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    if best is None:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    return best_move