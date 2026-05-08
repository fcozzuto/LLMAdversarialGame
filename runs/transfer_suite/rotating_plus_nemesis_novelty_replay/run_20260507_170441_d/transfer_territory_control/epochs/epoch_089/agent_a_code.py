def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    if opp_t:
        cx = sum(x for x, _ in opp_t) / len(opp_t)
        cy = sum(y for _, y in opp_t) / len(opp_t)
    else:
        cx, cy = ox, oy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Cell capture / invasion heuristic
        if (nx, ny) in opp_t:
            base = 8.0
        elif (nx, ny) in unclaimed:
            base = 5.0
        elif (nx, ny) in self_t:
            base = 1.0
        else:
            base = 0.5

        # Frontier bias: prefer approaching opponent territory center
        dist2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        approach = -0.03 * dist2

        # Break ties by preferring moves that reduce manhattan distance to opponent position
        manh = abs(nx - ox) + abs(ny - oy)
        tie = -0.01 * manh

        # Slight anti-stall: reward if we actually move (within bounds)
        moved = 0.02 if (dx != 0 or dy != 0) else 0.0

        score = base + approach + tie + moved

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]