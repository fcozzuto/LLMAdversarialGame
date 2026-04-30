def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not (0 <= sx < w and 0 <= sy < h) or (sx, sy) in obstacles:
        return [0, 0]

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    best = None
    bestd = None
    for x, y in resources:
        d = abs(x - sx) + abs(y - sy)
        if best is None or d < bestd or (d == bestd and (x, y) < best):
            best = (x, y)
            bestd = d

    tx, ty = best
    curd = abs(tx - sx) + abs(ty - sy)
    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = abs(tx - nx) + abs(ty - ny)
        score = (curd - nd) * 100 - nd
        if (nx, ny) in resources:
            score += 10000
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if all(isinstance(v, int) for v in best_move) else [0, 0]