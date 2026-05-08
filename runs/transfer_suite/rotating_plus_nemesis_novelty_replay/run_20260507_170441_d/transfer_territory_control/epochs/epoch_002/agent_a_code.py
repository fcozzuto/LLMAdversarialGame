def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", [])
    obs_set = set()
    for p in obstacles:
        try:
            x, y = p
            obs_set.add((int(x), int(y)))
        except:
            pass

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells", [])
    target = None
    bestd = None
    if unclaimed:
        for p in unclaimed:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if (x, y) in obs_set or not in_bounds(x, y):
                continue
            d = abs(x - sx) + abs(y - sy)
            if bestd is None or d < bestd or (d == bestd and (x, y) < target):
                bestd = d
                target = (x, y)

    if target is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        if abs(ox - sx) + abs(oy - sy) <= 3:
            tx, ty = ox, oy
        target = (tx, ty)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        dist = abs(target[0] - nx) + abs(target[1] - ny)
        # Extra mild preference: move that also moves away from obstacles isn't needed; just avoid staying if equal.
        away = abs(ox - nx) + abs(oy - ny)
        score = (dist, -away, abs(dx) + abs(dy), nx, ny)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs_set:
                return [dx, dy]
        return [0, 0]

    return [int(best[1]), int(best[2])]