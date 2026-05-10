def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    unT = observation.get("unclaimed_cells") or []
    targets = []
    for p in unT:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                targets.append((x, y))

    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    bestScore = None

    if targets:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            d = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
            score = -d
            if bestScore is None or score > bestScore or (score == bestScore and (nx, ny) < best):
                bestScore = score
                best = (nx, ny)
    else:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            score = - (abs(nx - ox) + abs(ny - oy))
            if bestScore is None or score > bestScore or (score == bestScore and (nx, ny) < best):
                bestScore = score
                best = (nx, ny)

    if best is None:
        return [0, 0]
    return [best[0] - sx, best[1] - sy]