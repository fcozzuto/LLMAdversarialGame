def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best = None
    best_score = -10**18

    def score_to(nx, ny):
        if (nx, ny) in obstacles:
            return -10**12
        if not (0 <= nx < w and 0 <= ny < h):
            return -10**12
        # Prefer moving closer to nearest resource
        if resources:
            dmin = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            s = -dmin
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            s = -(abs(nx - cx) + abs(ny - cy))
        # Avoid opponent by preferring farther distance
        do = abs(nx - ox) + abs(ny - oy)
        s += do * 0.2
        # Slightly avoid dead zones near obstacles
        near = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                tx, ty = nx + dx, ny + dy
                if (tx, ty) in obstacles:
                    near += 1
        s -= near * 0.1
        return s

    # Deterministic tie-break: fixed move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        s = score_to(nx, ny)
        if s > best_score:
            best_score = s
            best = [dx, dy]

    # Fallback (should never be None)
    if best is None:
        return [0, 0]
    return best