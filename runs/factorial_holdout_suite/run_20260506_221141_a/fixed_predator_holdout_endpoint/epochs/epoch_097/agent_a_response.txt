def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in obstacles_list:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    res = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            res.append((rx, ry))
    if not res:
        return [0, 0]

    if (sx, sy) in res:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_for_pos(px, py):
        best = None
        for (rx, ry) in res:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources we are not behind on; otherwise steal advantage if possible.
            key = (od - sd, -sd, -man(px, py, rx, ry))
            # If self is closer or equal, strongly prioritize it.
            if sd <= od:
                key = (od - sd + 1000, -sd)
            if best is None or key > best[0]:
                best = (key, rx, ry)
        return best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    scored = []
    for dx, dy, nx, ny in moves:
        b = best_for_pos(nx, ny)
        if b is None:
            continue
        key, rx, ry = b
        # Small penalty for staying still to keep progress unless already optimal.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        # Additional bias toward moving closer to chosen target.
        progress = -man(nx, ny, rx, ry)
        # Denier pressure: if opponent is closer to target than we are, prefer reducing that gap.
        gap = man(ox, oy, rx, ry) - man(nx, ny, rx, ry)
        scored.append(((key[0] + gap, key[1] + progress, -stay_pen), dx, dy))

    if not scored:
        return [0, 0]
    scored.sort(reverse=True)
    return [int(scored[0][1]), int(scored[0][2])]