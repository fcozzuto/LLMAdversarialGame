def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1)]
    if not valid(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best = None
        bestd = 10**9
        for x, y in resources:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd or (d == bestd and (x, y) < (best[0], best[1]) if best else False):
                bestd = d
                best = (x, y)
        tx, ty = best
        candidates = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                nd = abs(tx - nx) + abs(ty - ny)
                candidates.append((nd, abs(ox - nx) + abs(oy - ny), (dx, dy)))
        if candidates:
            candidates.sort()
            return [candidates[0][2][0], candidates[0][2][1]]

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            d = abs(ox - nx) + abs(oy - ny)
            candidates.append((d, (dx, dy)))
    if candidates:
        candidates.sort(key=lambda t: (t[0], t[1]))
        dx, dy = candidates[0][1]
        return [dx, dy]

    return [0, 0]