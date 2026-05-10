def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    targets = []
    for k in ("resources", "unclaimed_cells"):
        for p in observation.get(k) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    targets.append((x, y))
    if not targets:
        targets = [(w // 2, h // 2), (ox, oy)]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        md = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
        do = abs(nx - ox) + abs(ny - oy)
        score = md * 2 - do + (1 if (dx == 0 and dy == 0) else 0)
        if score < best[0]:
            best = (score, dx, dy)
    _, dx, dy = best
    return [int(dx), int(dy)]