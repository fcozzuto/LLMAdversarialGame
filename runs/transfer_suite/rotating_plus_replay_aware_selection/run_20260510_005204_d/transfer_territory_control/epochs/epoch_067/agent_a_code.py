def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    targets = []
    for k in ("unclaimed_cells", "resources"):
        for p in observation.get(k) or []:
            if p and len(p) >= 2:
                targets.append((int(p[0]), int(p[1])))
        if targets:
            break

    if not targets:
        targets = [(ox, oy)]

    targets = [t for t in targets if inb(t[0], t[1])]
    if not targets:
        targets = [(ox, oy)]
        if not inb(ox, oy):
            targets = [(0, 0)]

    tx, ty = min(targets, key=lambda t: (dist(sx, sy, t[0], t[1]), t[0], t[1]))

    best = None
    bestd = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist(nx, ny, tx, ty)
        if bestd is None or d < bestd or (d == bestd and (dx, dy) < best):
            bestd = d
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]