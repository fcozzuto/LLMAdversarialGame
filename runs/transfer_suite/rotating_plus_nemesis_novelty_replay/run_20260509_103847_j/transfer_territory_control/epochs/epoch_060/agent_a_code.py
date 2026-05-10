def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((dx, dy))
    if not candidates:
        return [0, 0]
    target = None
    bestd = None
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                d = abs(x - sx) + abs(y - sy)
                if bestd is None or d < bestd:
                    bestd, target = d, (x, y)
    if target is None:
        bestd = None
        for p in observation.get("unclaimed_cells") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    d = abs(x - sx) + abs(y - sy)
                    if bestd is None or d < bestd:
                        bestd, target = d, (x, y)
    if target is None:
        target = tuple(observation.get("opponent_position") or [w - 1, h - 1])
        tx, ty = int(target[0]), int(target[1])
    else:
        tx, ty = target
    best = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        d = abs(tx - nx) + abs(ty - ny)
        if best is None or d < best[0]:
            best = (d, dx, dy)
    return [best[1], best[2]]