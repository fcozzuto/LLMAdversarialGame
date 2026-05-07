def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", None) or []
    obstacles = observation.get("obstacles", None) or []
    if not resources:
        return [0, 0]

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0),
             (-1, -1), (-1, 1), (1, -1), (1, 1)]

    best = moves[0]
    bestv = -10**18
    tr = observation.get("turns_remaining", 0) or 0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue
        dres = 10**9
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) == 2:
                rx, ry = int(r[0]), int(r[1])
                d = md(nx, ny, rx, ry)
                if d < dres:
                    dres = d
        dop = md(nx, ny, ox, oy)
        v = -(dres * 10 + dop) if tr and tr <= 6 else -(dres * 10) + dop
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]