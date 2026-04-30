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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    sx = max(0, min(w - 1, sx))
    sy = max(0, min(h - 1, sy))
    ox = max(0, min(w - 1, ox))
    oy = max(0, min(h - 1, oy))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    if not resources or not inb(sx, sy):
        tx, ty = ox, oy
    else:
        tx, ty = min(resources, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))

    best = None
    bestd = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = abs(tx - nx) + abs(ty - ny)
        if d < bestd:
            bestd = d
            best = [dx, dy]
    return best if best is not None else [0, 0]