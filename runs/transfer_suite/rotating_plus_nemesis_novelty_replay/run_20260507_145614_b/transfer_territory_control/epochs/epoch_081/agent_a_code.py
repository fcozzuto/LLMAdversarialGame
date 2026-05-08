def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    targets = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))

    if not targets:
        for p in observation.get("resources") or []:
            if p and len(p) >= 2:
                x, y = p[0], p[1]
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    targets.append((x, y))
    if not targets and 0 <= ox < w and 0 <= oy < h and (ox, oy) not in obstacles:
        targets = [(ox, oy)]

    if targets:
        tx, ty = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    else:
        tx, ty = sx, sy

    moves = [(0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]
    best = None
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = abs(nx - tx) + abs(ny - ty)
            if best is None or d < best_d:
                best = [dx, dy]
                best_d = d
    if best is not None:
        return best

    return [0, 0] if (0 == 0 and 0 == 0) else [0, 0]