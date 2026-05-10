def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)
    unclaimed = observation.get("unclaimed_cells", []) or []
    uc = set((int(x), int(y)) for x, y in unclaimed)
    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory", []) or []))
    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory", []) or []))

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    # Aim: expand into unclaimed while staying mobile; mildly contest opponent by reducing distance
    best = [0, 0]
    best_score = -10**18

    # If we're far from any unclaimed, drift toward opponent to collide/flip
    if not uc:
        target_mode = 0
    else:
        d_self_unclaimed = min(abs(x - sx) + abs(y - sy) for x, y in uc)
        target_mode = 1 if d_self_unclaimed <= 6 else 0

    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Mobility after move
        mob = 0
        for ax, ay in neigh:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) not in obs:
                mob += 1

        score = 0
        if (nx, ny) in uc:
            score += 1200
        if (nx, ny) in oppT:
            # Flipping is allowed, but entering opponent territory too freely can be risky.
            # Only reward if it improves distance to opponent or opens mobility.
            score -= 450
            score += 40 if (abs(nx - ox) + abs(ny - oy)) < (abs(sx - ox) + abs(sy - oy)) else 0

        # Frontier preference: step closer to unclaimed but also adjacent to our territory
        if selfT:
            adj_self = any((nx + ax, ny + ay) in selfT for ax, ay in [(-1,0),(1,0),(0,-1),(0,1)])
            if adj_self:
                score += 160

        # Distance shaping
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_own = abs(nx - sx) + abs(ny - sy)  # always small; keeps tie-breaking stable
        score += (-10 * d_opp)
        if target_mode == 1 and uc:
            d_uc = min(abs(x - nx) + abs(y - ny) for x, y in uc)
            score += (-30 * d_uc)

        # Avoid low mobility traps
        score += 25 * mob

        # Deterministic tie-breaker (prefer smaller dx,dy order)
        if score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = [dx, dy]

    # If all moves invalid (unlikely), stay
    return best