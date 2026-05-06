def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 1))
    h = int(observation.get("grid_height", 1))

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            res.append((r[0], r[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    if res:
        tx, ty = min(res, key=lambda p: manhattan(sx, sy, p[0], p[1]))
        scored = []
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            scored.append((manhattan(nx, ny, tx, ty), manhattan(nx, ny, ox, oy), dx, dy))
        scored.sort()
        _, _, dx, dy = scored[0]
        return [int(dx), int(dy)]
    else:
        scored = []
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            scored.append((manhattan(nx, ny, ox, oy), abs(dx) + abs(dy), dx, dy))
        scored.sort()
        _, _, dx, dy = scored[0]
        return [int(dx), int(dy)]