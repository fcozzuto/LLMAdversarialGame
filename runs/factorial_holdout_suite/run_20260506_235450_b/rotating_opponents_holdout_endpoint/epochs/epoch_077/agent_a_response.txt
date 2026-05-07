def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    tr = int(observation.get("remaining_resource_count", 999) or 999)
    endgame = 1 if tr <= 4 else 0

    best = None
    best_key = None
    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # Race-aware: big weight to denying opponent in endgame; otherwise balance to avoid stalemates.
        adv = od - sd
        key = (adv * (10 if endgame else 6), -sd, -od, -x - y)
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    dx_t = 0 if tx == sx else (1 if tx > sx else -1)
    dy_t = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = cheb(nx, ny, tx, ty)
                # Prefer moves that reduce distance; in ties prefer moving toward target axes deterministically.
                align = 0
                if dx == dx_t:
                    align += 1
                if dy == dy_t:
                    align += 1
                candidates.append((d, -align, dx, dy))
    candidates.sort()
    return [int(candidates[0][2]), int(candidates[0][3])]