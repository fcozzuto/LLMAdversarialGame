def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    env = str(observation.get("environment_name", "")).lower()
    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()

    is_pursuer = ("pursu" in sr) or ("hunter" in sr)
    if "evasion" in env and (("evad" in sr) or ("escape" in sr) or ("runner" in sr)):
        is_pursuer = False
    if ("pursu" in orr) or ("hunter" in orr):
        is_pursuer = False
    if ("evad" in orr) or ("escape" in orr) or ("runner" in orr):
        is_pursuer = True

    def dist_cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d = dist_cheb(nx, ny)
            # pursuer: minimize distance, evader: maximize distance
            score = (-d if is_pursuer else d)
            # mild wall/obstacle adjacency bias to avoid getting stuck
            wall_pen = 0
            if nx in (0, w - 1): wall_pen += 0.05
            if ny in (0, h - 1): wall_pen += 0.05
            score -= wall_pen
            if best is None or (score > best_score):
                best = [dx, dy]
                best_score = score

    if best is not None:
        return [int(best[0]), int(best[1])]

    # fallback: try staying or minimal legal step that isn't blocked by obstacles
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [int(dx), int(dy)]
    return [0, 0]