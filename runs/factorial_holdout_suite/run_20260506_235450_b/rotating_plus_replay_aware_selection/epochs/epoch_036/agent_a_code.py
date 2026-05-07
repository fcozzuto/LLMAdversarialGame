def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best_target = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach first; otherwise best race.
        lead = do - ds
        key = (0 if lead > 0 else 1, -lead, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target
    best_move = None
    best_mkey = None
    for dx, dy, nx, ny in legal:
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(ox, oy, rx, ry)
        # Higher advantage, then shorter distance, then deterministic tie-break.
        adv = do2 - ds2
        mkey = (-adv, ds2, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]