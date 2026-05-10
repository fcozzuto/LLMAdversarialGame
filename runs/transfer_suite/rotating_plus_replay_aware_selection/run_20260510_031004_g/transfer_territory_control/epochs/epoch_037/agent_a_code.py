def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = observation.get("unclaimed_cells", None)
    if unclaimed is None:
        unclaimed = observation.get("unclaimed", [])
    unclaimed = set(map(tuple, unclaimed))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    free = lambda x, y: inb(x, y) and (x, y) not in obstacles

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda c: abs(sx - c[0]) + abs(sy - c[1]))
    else:
        tx, ty = px, py

    best = None
    best_score = -10**18
    best_tie = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        ds = abs(nx - tx) + abs(ny - ty)
        dp = abs(nx - px) + abs(ny - py)
        score = -ds * 3 + dp
        tie = (ds, -dp, dx, dy)
        if score > best_score or (score == best_score and (best_tie is None or tie < best_tie)):
            best_score = score
            best_tie = tie
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]