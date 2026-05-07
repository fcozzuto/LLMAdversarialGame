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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    if not valid(sx, sy):
        for dx, dy in dirs[1:]:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                res.append((x, y))

    if not res:
        # deterministic obstacle-aware drift toward opponent corner-ish
        tx = 0 if ox > w // 2 else w - 1
        ty = 0 if oy > h // 2 else h - 1
        best = None
        bestd = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = [dx, dy]
        return best if best is not None else [0, 0]

    # Evaluate each move by best "first-claim" margin across resources
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        move_val = -10**18
        for rx, ry in res:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # prefer resources where we are closer; break ties by favoring shorter absolute distance
            val = (do - ds) * 1000 - ds
            if val > move_val:
                move_val = val
        # small bias to not wander when tied
        move_val -= (man(nx, ny, sx, sy)) * 1
        if move_val > best_val:
            best_val = move_val
            best_move = [dx, dy]
    return best_move