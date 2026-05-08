def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    targets = []
    for c in (observation.get("resources") or []):
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))
    if not targets:
        for c in (observation.get("unclaimed_cells") or []):
            if c and len(c) >= 2:
                x, y = int(c[0]), int(c[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    targets.append((x, y))

    if not targets:
        cand = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    tx, ty = None, None
    bestd = 10**9
    for x, y in targets:
        d = abs(x - sx) + abs(y - sy)
        if d < bestd:
            bestd = d
            tx, ty = x, y

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = abs(tx - nx) + abs(ty - ny)
        score = (d, -abs(nx - (observation.get("opponent_position") or [0, 0])[0]) - abs(ny - (observation.get("opponent_position") or [0, 0])[1]))
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]