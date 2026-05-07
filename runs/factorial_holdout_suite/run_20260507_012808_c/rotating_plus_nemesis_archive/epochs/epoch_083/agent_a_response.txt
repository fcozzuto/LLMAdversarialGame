def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def quad_score(p):
        x, y = p
        return (1 if x >= w // 2 else 0) * 2 + (1 if y >= h // 2 else 0)

    turn = int(observation.get("turn_index", 0) or 0)

    legal_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal_moves.append((dx, dy))
    if not legal_moves:
        return [0, 0]

    best = None
    for r in resources:
        self_d = cheb((sx, sy), r)
        opp_d = cheb((ox, oy), r)
        rel = opp_d - self_d  # larger => we are relatively closer
        q = quad_score(r)
        pref = q - ((turn // 2) % 4) * 0.01  # deterministic quadrant drift
        key = (rel, -self_d, pref, (r[0] * 31 + r[1]) % 97)
        if best is None or key > best[0]:
            best = (key, r)

    _, target = best
    tx, ty = target

    # Choose a legal move that best reduces chebyshev distance; break ties toward diagonal.
    best_move = (0, 0)
    best_key = None
    for dx, dy in legal_moves:
        nx, ny = sx + dx, sy + dy
        d = cheb((nx, ny), (tx, ty))
        diag = 1 if dx != 0 and dy != 0 else 0
        # slight preference to moves aligning with target
        align = (1 if dx == (1 if tx > sx else (-1 if tx < sx else 0)) else 0) + (1 if dy == (1 if ty > sy else (-1 if ty < sy else 0)) else 0)
        key = (-d, diag, align, (dx + 2) * 7 + (dy + 2))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]