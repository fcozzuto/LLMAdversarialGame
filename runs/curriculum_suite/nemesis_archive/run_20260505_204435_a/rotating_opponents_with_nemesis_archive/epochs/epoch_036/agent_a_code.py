def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = sp if isinstance(sp, (list, tuple)) and len(sp) >= 2 else (0, 0)
    ox, oy = op if isinstance(op, (list, tuple)) and len(op) >= 2 else (0, 0)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    def get_pos(item):
        if isinstance(item, dict):
            pos = item.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                return pos[0], pos[1]
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            return item[0], item[1]
        return None

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        p = get_pos(r)
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and legal(x, y):
                targets.append((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    if targets:
        tx, ty = min(targets, key=lambda t: (man(sx, sy, t[0], t[1]), t[0], t[1]))
    else:
        tx, ty = ox, oy

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        val = d
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]