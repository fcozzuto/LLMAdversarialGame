def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]

    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    center = ((w - 1) / 2.0, (h - 1) / 2.0)
    best_score = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        pos = (nx, ny)
        # Base gain: prioritize capturing opponent territory, then unclaimed, then expanding our own
        if pos in opp_terr:
            gain = 1.6
        elif pos in unclaimed:
            gain = 1.0
        elif pos in self_terr:
            gain = 0.25
        else:
            gain = 0.35

        # Risk: opponent could be able to respond; prefer moves that increase distance to opponent
        d_before = man((sx, sy), (ox, oy))
        d_after = man((nx, ny), (ox, oy))
        dist_term = (d_after - d_before) * 0.18

        # Boundary pressure: if move is near opponent territory, slightly encourage it if it also captures/claims
        adj_opp = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if inb(px, py) and (px, py) in opp_terr:
                    adj_opp += 1
        boundary_term = (adj_opp / 8.0) * (0.25 if gain >= 1.0 else -0.15)

        # Centering to avoid getting stuck at corners; deterministic, mild
        cx, cy = center
        dist_center = abs(nx - cx) + abs(ny - cy)
        center_term = -dist_center * 0.03

        # Deterministic tie-breaker: prefer lexicographically smaller move
        total = gain + dist_term + boundary_term + center_term
        if best_score is None or total > best_score or (total == best_score and (dx, dy) < tuple(best_move)):
            best_score = total
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]