def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort()

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if resources:
        best = None
        bestd = 10**9
        for tx, ty in resources:
            d = abs(tx - sx) + abs(ty - sy)
            if d < bestd or (d == bestd and (tx, ty) < best):
                bestd = d
                best = (tx, ty)
        tx, ty = best
        scored = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dist = abs(tx - nx) + abs(ty - ny)
            scored.append((dist, abs(ox - nx) + abs(oy - ny), dx, dy))
        scored.sort()
        if scored:
            return [scored[0][2], scored[0][3]]
        return [0, 0]

    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        scored.append((-dist, nx, ny, dx, dy))
    scored.sort()
    if scored:
        return [scored[0][3], scored[0][4]]
    return [0, 0]