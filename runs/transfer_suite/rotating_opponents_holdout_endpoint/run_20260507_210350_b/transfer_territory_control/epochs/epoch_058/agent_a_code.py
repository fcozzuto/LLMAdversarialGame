def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    rem = int(observation.get("remaining_resource_count") or (len(resources) if resources else 0))
    targets = resources if rem > 0 else [(ox, oy)]
    if not targets:
        targets = [(ox, oy)]

    def md(nx, ny, tx, ty):
        return abs(nx - tx) + abs(ny - ty)

    best = (10**9, 10**9, 10**9)
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = min(md(nx, ny, tx, ty) for tx, ty in targets)
        # Prefer not to stay; then prefer smaller dx^2+dy^2 (more decisive moves); tie-break by dx,dy.
        stay_pen = 0 if (dx == 0 and dy == 0) else -1
        move_spread = dx * dx + dy * dy
        cand = (d, stay_pen, -move_spread)
        if cand < best:
            best = cand
            best_move = (dx, dy)

    if not inb(sx + best_move[0], sy + best_move[1]):
        # Fallback: any valid move, else stay.
        for dx, dy in dirs:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return [best_move[0], best_move[1]]