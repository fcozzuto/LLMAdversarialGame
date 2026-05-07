def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_toward(tx, ty):
        candidates = []
        for dx, dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Prefer reducing distance to target; break ties by moving generally toward it.
            dist = cd(nx, ny, tx, ty)
            toward = abs(nx - tx) + abs(ny - ty)
            candidates.append((dist, toward, dx, dy))
        candidates.sort()
        return [candidates[0][2], candidates[0][3]] if candidates else [0, 0]

    if not resources:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Pick resource where we are comparatively closer than the opponent.
    best = None
    for rx, ry in resources:
        myd = cd(sx, sy, rx, ry)
        opd = cd(ox, oy, rx, ry)
        # Primary: maximize (opponent distance - my distance)
        # Secondary: minimize my distance (arrive sooner if competitive)
        key = (opd - myd, -opd, -myd)  # sorted ascending later, so invert appropriately
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    nx, ny = sx + dx, sy + dy
    if inb(nx, ny) and (nx, ny) not in obstacles:
        return [dx, dy]
    return step_toward(tx, ty)