def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) + [0, 0])[:2]
    ox, oy = (observation.get("opponent_position", [w - 1, h - 1]) + [w - 1, h - 1])[:2]
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(xy) for xy in (observation.get("unclaimed_cells", []) or []))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]

    def mdist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def opp_d(x, y):
        if not opp_cells:
            return mdist((x, y), (ox, oy))
        best = 10**9
        for (px, py) in opp_cells:
            d = abs(x - px) + abs(y - py)
            if d < best:
                best = d
        return best

    # Prefer expanding from our frontier into unclaimed.
    candidates = []
    for (x, y) in self_cells:
        for dx, dy in neigh4:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                candidates.append((nx, ny))
    if not candidates:
        candidates = [c for c in unclaimed if c not in obstacles and inb(c[0], c[1])]

    if not candidates:
        return [0, 0]

    # Deterministic scoring: expand towards far-from-opponent territory.
    opp_center = (ox, oy)
    best = None
    best_score = None
    for (tx, ty) in candidates:
        d_me = abs(tx - sx) + abs(ty - sy)
        d_opp = opp_d(tx, ty)
        d_opp_center = mdist((tx, ty), opp_center)
        # Slight bias to smaller distance-to-target after maximizing safety.
        score = (d_opp, d_opp_center, -d_me)
        if best is None or score > best_score:
            best = (tx, ty)
            best_score = score

    tx, ty = best
    best_move = (0, 0)
    best_step_score = None
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        step = (abs(nx - tx) + abs(ny - ty), -opp_d(nx, ny))
        if best_step_score is None or step < best_step_score:
            best_step_score = step
            best_move = (dx, dy)

    # If all moves blocked, stay.
    return [int(best_move[0]), int(best_move[1])]