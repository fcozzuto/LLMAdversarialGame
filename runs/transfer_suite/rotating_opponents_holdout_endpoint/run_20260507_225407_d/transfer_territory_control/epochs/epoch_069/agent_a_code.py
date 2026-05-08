def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
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
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    want = None
    if resources:
        best = None
        bestd = None
        for x, y in resources:
            d = abs(x - sx) + abs(y - sy)
            if bestd is None or d < bestd:
                bestd = d
                best = (x, y)
        want = best

    def score(nx, ny):
        s = 0
        if want is not None:
            s += (1000 - (abs(want[0] - nx) + abs(want[1] - ny)))
        dfo = abs(ox - nx) + abs(oy - ny)
        s += dfo
        if (nx, ny) == (ox, oy):
            s -= 100000
        return s

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = score(nx, ny)
        if best_score is None or sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]