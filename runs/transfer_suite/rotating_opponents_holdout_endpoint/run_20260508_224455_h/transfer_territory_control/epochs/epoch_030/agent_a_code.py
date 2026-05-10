def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_ter = set(map(tuple, observation.get("self_territory", []) or []))
    opp_ter = set(map(tuple, observation.get("opponent_territory", []) or []))
    oxpos, oypos = observation.get("opponent_position", [w - 1, h - 1])

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_score(x, y):
        # Reward moving into/near contested territory while driving toward center.
        center_dist = abs(x - cx) + abs(y - cy)
        base = -center_dist

        if (x, y) in self_ter:
            base += 0.4
        if (x, y) in opp_ter:
            base += 1.6  # flipping on entry => good to steal
        # If unclaimed exists, move toward the best one (closest to center)
        if unclaimed:
            # Only consider a few deterministic candidates: those closest to center, then to our position
            # (avoid full-grid search complexity).
            best_un = None
            best_key = None
            for (ux, uy) in unclaimed:
                k1 = abs(ux - cx) + abs(uy - cy)
                k2 = abs(ux - sx) + abs(uy - sy)
                k = (k1, k2)
                if best_key is None or k < best_key:
                    best_key = k
                    best_un = (ux, uy)
            ux, uy = best_un
            base += -((abs(ux - x) + abs(uy - y)) * 0.9)
            base += -best_key[0] * 0.05  # slight preference for central targets globally
        # Minor objective: avoid getting too close to opponent position early
        base += (abs(x - oxpos) + abs(y - oypos)) * 0.02
        return base

    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            val = -10.0  # likely rejected by engine staying; heavily penalize
        else:
            val = cell_score(nx, ny)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]