def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    rset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                rset.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("chaser" in self_role) or ("pursue" in self_role)
    # If we are the pursuer, minimize distance to capture; otherwise, maximize distance.
    minimize = is_pursuer

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_val = None
    tiebreak = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in rset:
            val = cheb(sx, sy, ox, oy)  # rejected/kept in place => same as current
        else:
            val = cheb(nx, ny, ox, oy)

        # Add a small deterministic penalty/bonus for obstacle adjacency to encourage lanes.
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in rset:
                    adj_pen += 1

        # Composite score: pursuer wants smaller; evader wants larger.
        score = val + (adj_pen * (0.02 if minimize else -0.02))

        # Capture if landing on opponent (cheb==0).
        if val == 0:
            score = score - (1e3 if minimize else -1e3)

        if best_val is None:
            best_val = score
            best = (dx, dy)
            tiebreak = (dx, dy)
        else:
            better = score < best_val if minimize else score > best_val
            if better:
                best_val = score
                best = (dx, dy)
                tiebreak = (dx, dy)
            elif score == best_val:
                # Deterministic tie-break: prefer smaller |dx|+|dy|, then lexicographic.
                cur_d = abs(dx) + abs(dy)
                best_d = abs(best[0]) + abs(best[1])
                if cur_d < best_d or (cur_d == best_d and (dx, dy) < best):
                    best = (dx, dy)

    return [int(best[0]), int(best[1])]