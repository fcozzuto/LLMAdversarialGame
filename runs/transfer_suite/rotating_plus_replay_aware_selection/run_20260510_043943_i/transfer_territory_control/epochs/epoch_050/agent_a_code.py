def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    targets = []
    for key in ("resources", "unclaimed_cells"):
        for p in observation.get(key, []) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y):
                    targets.append((x, y))
        if targets:
            break

    if not targets:
        targets = [(ox, oy)]

    def dist(x, y):
        return abs(x - sx) + abs(y - sy)

    targets.sort(key=lambda t: (dist(t[0], t[1]), t[0], t[1]))
    tx, ty = targets[0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        score = (d, abs(ny - ty), abs(nx - tx))
        if best is None or score < best[0]:
            best = (score, [dx, dy])
    if best is None:
        return [0, 0]
    return best[1]