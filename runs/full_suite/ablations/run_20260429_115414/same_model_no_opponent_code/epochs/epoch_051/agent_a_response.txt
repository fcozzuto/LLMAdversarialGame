def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if resources:
        def key(r):
            x, y = r
            man = abs(x - sx) + abs(y - sy)
            diag = abs(x - sx - (y - sy))  # prefers alignment along main diagonal-ish
            return (man, diag, x, y)
        tx, ty = min(resources, key=key)

        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            dist = abs(tx - nx) + abs(ty - ny)
            # Prefer moves that reduce distance; small deterministic bias toward moving.
            step_cost = 0 if (dx == 0 and dy == 0) else 1
            cand = (dist, step_cost, dx, dy)
            if cand < best:
                best = cand
        return [int(best[2]), int(best[3])]

    # No visible resources: drift toward nearest corner to create deterministic pattern.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    cx, cy = min(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    best = (10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = abs(cx - nx) + abs(cy - ny)
        step_cost = 0 if (dx == 0 and dy == 0) else 1
        cand = (dist, step_cost, dx, dy)
        if cand < best:
            best = cand
    return [int(best[2]), int(best[3])]