def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return (dx if dx >= 0 else -dx) if (dx if dx >= 0 else -dx) >= (dy if dy >= 0 else -dy) else (dy if dy >= 0 else -dy)

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if nx == ox and ny == oy:
            return [dx, dy]
        d0 = cheb(sx, sy, ox, oy)
        d1 = cheb(nx, ny, ox, oy)
        man_inc = (abs(nx - ox) + abs(ny - oy)) - (abs(sx - ox) + abs(sy - oy))
        # Prefer smaller distance; avoid increasing distance; tie-break deterministically.
        key = (d1, abs(man_inc), man_inc if man_inc > 0 else 0, dx, dy)
        if best is None or key < best_key:
            best = [dx, dy]
            best_key = key

    if best is None:
        return [0, 0]
    return best