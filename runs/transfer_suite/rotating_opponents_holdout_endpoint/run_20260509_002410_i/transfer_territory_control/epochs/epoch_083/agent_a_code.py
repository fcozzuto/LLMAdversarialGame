def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                targets.append((x, y))
    if not targets:
        # No unclaimed: move toward away from opponent slightly while staying valid
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if d > bestv:
                bestv = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    tx, ty = targets[0]
    md = abs(sx - tx) + abs(sy - ty)
    for x, y in targets[1:]:
        d = abs(sx - x) + abs(sy - y)
        if d < md:
            md = d
            tx, ty = x, y

    best = (0, 0)
    bestv = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        # Prefer getting closer to target; tiebreak by being farther from opponent
        v = -d * 1000 + (abs(nx - ox) + abs(ny - oy))
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]