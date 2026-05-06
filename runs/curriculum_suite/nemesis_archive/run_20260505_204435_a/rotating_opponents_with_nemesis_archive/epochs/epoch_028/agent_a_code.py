def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)

    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    def parse_pos(r):
        if isinstance(r, dict):
            pos = r.get("position", None)
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                return (pos[0], pos[1])
            return None
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return (r[0], r[1])
        return None

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        p = parse_pos(r)
        if p is not None:
            targets.append(p)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    if not legal(sx, sy):
        for dx, dy in dirs:
            if legal(sx + dx, sy + dy):
                return [int(dx), int(dy)]
        return [0, 0]

    if targets:
        best_move = (0, 0)
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            dself = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
            dop = min(abs(ox - tx) + abs(oy - ty) for tx, ty in targets)
            val = (dself - dop, abs(nx - ox) + abs(ny - oy))
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_d = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = abs(nx - cx) + abs(ny - cy)
        if best_d is None or d < best_d:
            best_d = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]