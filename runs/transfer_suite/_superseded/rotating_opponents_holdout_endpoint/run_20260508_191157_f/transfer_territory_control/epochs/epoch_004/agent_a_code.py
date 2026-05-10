def choose_move(observation):
    sx, sy = observation["self_position"]
    gx, gy = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    opponent_territory = observation.get("opponent_territory") or []
    targets = opponent_territory if opponent_territory else (observation.get("unclaimed_cells") or [])
    if not targets:
        return [0, 0]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer short deterministic list of candidate deltas (incl. diagonals, then stay)
    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Precompute obstacle "clearance" weights around our local area
    def clearance(p):
        if not obstacles:
            return 0
        best = 999
        for (ox, oy) in obstacles:
            d = abs(ox - p[0]) + abs(oy - p[1])
            if d < best:
                best = d
                if best <= 1:
                    break
        return best

    # Targeting: if we are behind, attack opponent territory; else claim near opponent border via unclaimed
    if observation.get("self_territory_count", 0) < observation.get("opponent_territory_count", 0) and opponent_territory:
        targets = opponent_territory
    elif not opponent_territory:
        pass
    else:
        # Use a smaller, deterministic subset of opponent territory closest to us to avoid drift
        tlist = sorted(targets, key=lambda p: manh((sx, sy), p))
        targets = tlist[:8] if len(tlist) > 8 else tlist

    best_move = [0, 0]
    best_score = 10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= gx or ny >= gy:
            continue
        if (nx, ny) in obstacles:
            continue
        newp = (nx, ny)

        # Distance to nearest target (lower is better)
        mind = 10**9
        for t in targets:
            d = abs(t[0] - nx) + abs(t[1] - ny)
            if d < mind:
                mind = d
                if mind == 0:
                    break

        # Obstacle clearance (higher is better)
        clr = clearance(newp)

        # Tie-breakers: prefer advancing towards map center to avoid getting stuck on edges
        center = (gx // 2, gy // 2)
        center_adv = abs(center[0] - sx) + abs(center[1] - sy) - (abs(center[0] - nx) + abs(center[1] - ny))

        # Weighted score: primarily minimize distance to targets, then maximize clearance, then maximize center advancement
        score = mind * 1000 - clr * 10 - center_adv
        if score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move