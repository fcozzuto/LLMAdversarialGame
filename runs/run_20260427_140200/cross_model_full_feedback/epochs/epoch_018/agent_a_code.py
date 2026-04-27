def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not candidates:
        return [0, 0]

    if resources:
        tx, ty = min(resources, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    else:
        tx, ty = ox, oy

    best = None
    bestd = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        d = abs(tx - nx) + abs(ty - ny)
        if best is None or d < bestd or (d == bestd and (dx, dy) < best):
            bestd = d
            best = (dx, dy)

    return [int(best[0]), int(best[1])]