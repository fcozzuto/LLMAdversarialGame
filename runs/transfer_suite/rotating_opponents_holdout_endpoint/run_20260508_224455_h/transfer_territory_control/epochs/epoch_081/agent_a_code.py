def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

    def make_set(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obst = make_set(observation.get("obstacles"))
    selfT = make_set(observation.get("self_territory"))
    unclaimed = make_set(observation.get("unclaimed_cells"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny): 
            continue
        if (nx, ny) in obst:
            continue
        v = 0
        v -= dist(nx, ny, ox, oy) * 2
        if (nx, ny) in unclaimed:
            v += 120
        if (nx, ny) in selfT:
            v -= 8
        if (nx, ny) == (ox, oy):
            v += 80
        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best