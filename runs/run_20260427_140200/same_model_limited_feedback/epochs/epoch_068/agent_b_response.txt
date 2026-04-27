def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def dist(a, b): 
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_score = None

    if resources:
        # Choose the move that minimizes (our distance to contested resource minus opponent distance)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            if (nx, ny) in obstacles:
                continue
            local_best = None
            for r in resources:
                our_d = abs(nx - r[0]) + abs(ny - r[1])
                opp_d = abs(ox - r[0]) + abs(oy - r[1])
                # Prefer resources we reach sooner; tie-break by closer to us
                key = (our_d - opp_d, our_d)
                if local_best is None or key < local_best:
                    local_best = key
            if local_best is None:
                continue
            # Convert key to a maximization score
            score = -(local_best[0] * 1000 + local_best[1])
            if best_score is None or score > best_score:
                best_score, best = score, (dx, dy)
            elif score == best_score:
                # Deterministic tie-break: smallest dx, then smallest dy
                if (dx, dy) < best:
                    best = (dx, dy)
    else:
        # No resources: drift toward center while also not suiciding into obstacles
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            if (nx, ny) in obstacles:
                continue
            score = -((nx - cx) ** 2 + (ny - cy) ** 2)
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
                best_score, best = score, (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]