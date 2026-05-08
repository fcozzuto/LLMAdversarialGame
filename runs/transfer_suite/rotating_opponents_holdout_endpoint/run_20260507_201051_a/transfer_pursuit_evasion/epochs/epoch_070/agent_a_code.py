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

    sr = (observation.get("self_role") or "").lower()
    orr = (observation.get("opponent_role") or "").lower()
    is_evader = ("evad" in sr) or ("escape" in sr) or ("runner" in sr) or ("evad" in orr)
    is_pursuer = ("purs" in sr) and not is_evader
    if not is_pursuer and not is_evader:
        env = (observation.get("environment_name") or "").lower()
        if "evasion" in env:
            is_evader = ("evad" in orr) or ("escape" in orr) or ("runner" in orr)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if is_pursuer:
            # pursue: minimize distance, then prefer progressing in x/y deterministically
            key = (-d, nx + ny * w)  # maximize -d => minimize d; tie-break fixed
        else:
            # evade: maximize distance, then prefer farther-from-opponent direction
            key = (d, (w - 1 - nx) + (h - 1 - ny) * w)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]