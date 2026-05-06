def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    if not resources:
        return [0, 0]

    def steps(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def best_cell():
        candidates = []
        for rx, ry in resources:
            sd = steps((sx, sy), (rx, ry))
            od = steps((ox, oy), (rx, ry))
            # Prefer targets we can reach first; otherwise prefer those that deny opponent more.
            # Tie-break deterministically by (rx,ry).
            score = (0, 0, 0, 0, 0)
            if sd < od:
                score = (0, sd, -od, rx, ry)
            elif sd == od:
                score = (1, sd, -od, rx, ry)
            else:
                score = (2, od - sd, -sd, rx, ry)
            candidates.append((score, rx, ry))
        candidates.sort(key=lambda t: t[0])
        return (candidates[0][1], candidates[0][2])

    target = best_cell()
    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (10**9, 10**9, 10**9)
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        sd = steps((nx, ny), target)
        od = steps((ox, oy), target)
        # If we can still stay competitive vs opponent, prefer faster approach; else choose least-bad.
        ahead = -1 if sd < od else (0 if sd == od else 1)
        # Deterministic tie-break by nx,ny
        key = (ahead, sd, nx * 16 + ny)
        if key < best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]