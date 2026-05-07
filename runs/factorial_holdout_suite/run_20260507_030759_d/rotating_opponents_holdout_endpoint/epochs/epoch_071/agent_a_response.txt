def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not inb(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    valid_res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                valid_res.append((x, y))
    if not valid_res:
        return [0, 0]

    best = None
    best_key = None
    for x, y in valid_res:
        sd = dist(sx, sy, x, y)
        od = dist(ox, oy, x, y)
        adv = od - sd
        key = (adv, -sd, -x, -y)  # deterministic ties
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd_new = dist(nx, ny, tx, ty)
        od = dist(ox, oy, tx, ty)
        adv_new = od - sd_new
        score = (adv_new, -sd_new, -nx, -ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]