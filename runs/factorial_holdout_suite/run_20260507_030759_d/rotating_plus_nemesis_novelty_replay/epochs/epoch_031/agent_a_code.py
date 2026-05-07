def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    res = observation.get("resources", None)
    resources = []
    if isinstance(res, (list, tuple)):
        for r in res:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                resources.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        resources = [(sx, sy)]

    def nearest_dist(x, y):
        best = 10**9
        for rx, ry in resources:
            d = abs(rx - x) + abs(ry - y)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dres = nearest_dist(nx, ny)
        dop = abs(ox - nx) + abs(oy - ny)
        val = -dres + 0.15 * dop
        if (nx, ny) == (ox, oy):
            val -= 1000
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]