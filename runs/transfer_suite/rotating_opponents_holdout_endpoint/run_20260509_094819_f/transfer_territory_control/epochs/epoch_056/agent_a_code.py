def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    (sx, sy) = observation.get("self_position") or (0, 0)
    (ox, oy) = observation.get("opponent_position") or (w - 1, h - 1)

    obs_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs_list if p is not None and len(p) == 2)

    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []

    targets = []
    for p in unclaimed:
        if p is not None and len(p) == 2:
            targets.append(tuple(p))
    if not targets:
        for p in resources:
            if p is not None and len(p) == 2:
                targets.append(tuple(p))
    if not targets:
        targets.append((ox, oy))

    tx, ty = targets[0]
    bestd = None
    for x, y in targets:
        d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
        if bestd is None or d < bestd:
            bestd = d
            tx, ty = x, y

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    cx, cy = sx, sy
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = cx + dx, cy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        score = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]