def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        tx, ty = ox, oy
    best = None
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        score = -(abs(nx - tx) + abs(ny - ty))
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]