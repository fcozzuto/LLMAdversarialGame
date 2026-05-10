def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "pursuer").lower()
    pursuer = (role != "evader")

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for a in observation.get("resources") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    target = (ox, oy)
    if resources:
        best = resources[0]
        bd = max(abs(sx - best[0]), abs(sy - best[1]))
        for r in resources[1:]:
            d = max(abs(sx - r[0]), abs(sy - r[1]))
            if d < bd:
                bd = d
                best = r
        target = best

    tx, ty = target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = max(abs(nx - tx), abs(ny - ty))
        val = dist if pursuer else -dist
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_m):
            best_val = val
            best_m = (dx, dy)

    if best_val is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                return [dx, dy]
        return [0, 0]
    return [best_m[0], best_m[1]]