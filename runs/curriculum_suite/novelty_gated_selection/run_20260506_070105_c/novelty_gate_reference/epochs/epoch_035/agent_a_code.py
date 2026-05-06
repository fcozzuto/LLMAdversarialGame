def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def score_target(rx, ry):
        d_me = man(sx, sy, rx, ry)
        d_op = man(ox, oy, rx, ry)
        # Prefer targets we can reach sooner; tie-break by absolute closeness.
        # Add small preference for further opponent disadvantage.
        return (0 if d_me < d_op else 1, - (d_op - d_me), d_me, rx, ry)

    rx, ry = min(res, key=lambda t: score_target(t[0], t[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            # Greedy: minimize distance to chosen resource; deterministically tie-break.
            v = (man(nx, ny, rx, ry), abs(nx - rx) + abs(ny - ry), dx, dy)
            if best is None or v < best[0]:
                best = (v, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]