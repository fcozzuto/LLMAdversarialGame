def choose_move(observation):
    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return 0, 0

    def inb(x, y, w, h):
        return 0 <= x < w and 0 <= y < h

    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = xy(observation.get("self_position", [0, 0]))
    ox, oy = xy(observation.get("opponent_position", [7, 7]))
    resources = [xy(r) for r in (observation.get("resources", []) or [])]
    obstacles = set(xy(o) for o in (observation.get("obstacles", []) or []))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    def cheb(a, b):
        return max(abs(b[0] - a[0]), abs(b[1] - a[1]))

    # If no visible resources, head to the center-adjacent line while avoiding obstacles,
    # with a bias toward the corner closer to resources would be ideal, but here we stabilize deterministically.
    if not resources:
        candidates = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny, w, h) and (nx, ny) not in obstacles:
                # Favor moving toward opponent if we are far (deny pathing), else toward center.
                to_op = cheb((nx, ny), (ox, oy))
                to_center = abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)
                val = (to_op * 0.1) - to_center
                candidates.append((val, dx, dy, nx, ny))
        if not candidates:
            return [0, 0]
        candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
        return [candidates[0][1], candidates[0][2]]

    # Evaluate next move by resulting advantage over best resource, with obstacle-aware tie-break.
    best_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny, w, h) or (nx, ny) in obstacles:
            continue

        # Advantage: how much closer we are than opponent (negative means worse).
        # Also include small preference to shorten our distance to avoid stalling.
        local_best = -10**9
        for rx, ry in resources:
            self_d = cheb((nx, ny), (rx, ry))
            opp_d = cheb((ox, oy), (rx, ry))
            adv = opp_d - self_d
            # If we can reach very quickly, prioritize strongly; deterministic tie-break by coordinates.
            val = adv * 10 - self_d
            # Tiny bias to pick lower (rx,ry) deterministically when val ties
            val -= (rx * 0.001 + ry * 0.0001)
            if val > local_best:
                local_best = val

        # Additional term: keep away from obstacles by preferring moves that have more free neighboring cells.
        free_n = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty, w, h) and (tx, ty) not in obstacles:
                free_n += 1
        score = local_best + free_n * 0.05
        best_moves.append((score, dx, dy))

    if not best_moves:
        return [0, 0]
    best_moves.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [best_moves[0][1], best_moves[0][2]]