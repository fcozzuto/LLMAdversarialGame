def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        # Chebyshev distance suits diagonal movement
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**9

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            self_d = 10**9
            opp_d = 10**9
            # pick best target for this move (maximizing advantage)
            for rx, ry in resources:
                sd = dist((nx, ny), (rx, ry))
                od = dist((ox, oy), (rx, ry))
                if sd < self_d or (sd == self_d and od < opp_d):
                    self_d = sd
                    opp_d = od
            # prefer being closer than opponent; tie-break with smaller self_d
            score = (opp_d - self_d) * 100 - self_d
            # deterministic tie-break: based on resulting position
            score += (nx * 3 + ny)
            if score > best_score:
                best_score = score
                best = [dx, dy]
        if best is not None:
            return best

    # Fallback: go toward center while avoiding obstacles
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # minimize distance to center, deterministic tie-break
        d = max(abs(nx - cx), abs(ny - cy))
        score = -d * 1000 + (nx * 3 + ny)
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]