def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # If no visible resources, move to reduce distance to opponent corner-funnel
        tx, ty = (w - 1, h - 1) if (ox + oy) < (sx + sy) else (0, 0)
        best = None
        bestd = 10**9
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = dist((nx, ny), (tx, ty))
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose moves that maximize "can-get-there-first" margin for some resource.
    # Margin = opp_dist - my_dist (higher means I'm closer).
    # Deterministic tie-break: prefer closer-to-some-resource, then lower dx/dy lexicographic.
    best_move = None
    best_score = -10**9
    best_alt_d = 10**9

    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        my = (nx, ny)
        local_best = -10**9
        local_alt = 10**9
        for r in resources:
            md = dist(my, r)
            od = dist((ox, oy), r)
            margin = od - md
            if margin > local_best:
                local_best = margin
                local_alt = md
            elif margin == local_best and md < local_alt:
                local_alt = md
        # Penalize drifting away from all resources slightly
        score = local_best * 1000 - local_alt
        if (score > best_score) or (score == best_score and local_alt < best_alt_d) or (score == best_score and local_alt == best_alt_d and (dx, dy) < best_move):
            best_score = score
            best_alt_d = local_alt
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]