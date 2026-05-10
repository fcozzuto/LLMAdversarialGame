def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    oppT = set((int(t[0]), int(t[1])) for t in (observation.get("opponent_territory") or []) if t and len(t) >= 2)
    myT = set((int(t[0]), int(t[1])) for t in (observation.get("self_territory") or []) if t and len(t) >= 2)
    unC = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)

    cx, cy = (W - 1) // 2, (H - 1) // 2
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obs or not inb(nx, ny):
            continue

        # Base: prefer central, stable presence
        dist_center = abs(nx - cx) + abs(ny - cy)
        score = -dist_center

        # Territory effects
        if (nx, ny) in oppT:
            score += 1200  # immediate flip
        elif (nx, ny) in unC:
            score += 140   # expansion into frontier
        elif (nx, ny) in myT:
            score += 20    # hold ground

        # Heuristic: move closer to opponent if we're adjacent to their claimed area
        if (nx, ny) not in obs:
            # count adjacent opponent cells after move
            adj_opp = 0
            for ax, ay in moves[:-1]:
                x2, y2 = nx + ax, ny + ay
                if inb(x2, y2) and (x2, y2) in oppT:
                    adj_opp += 1
            score += adj_opp * 80

            # avoid stepping next to too many obstacles (risk of being penned)
            adj_obs = 0
            for ax, ay in moves[:-1]:
                x2, y2 = nx + ax, ny + ay
                if inb(x2, y2) and (x2, y2) in obs:
                    adj_obs += 1
            score -= adj_obs * 10

        # If we can grab opponent territory, prioritize deterministically
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move