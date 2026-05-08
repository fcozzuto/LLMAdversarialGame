def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_self = str(observation.get("self_role") or "").lower()
    role_opp = str(observation.get("opponent_role") or "").lower()

    running = ("evader" in role_self) or ("runner" in role_self) or ("escape" in role_self)
    if ("pursuer" in role_self) or ("catcher" in role_self):
        running = False
    if ("evader" in role_opp):
        running = True

    obstacles = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = d if running else -d
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    return [0, 0] if best is None else [int(best[0]), int(best[1])]