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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh8 = dirs

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    # Build a "frontier" of unclaimed cells adjacent to opponent territory; aim to grab it.
    opp_frontier = set()
    if opp_t and unclaimed:
        for (x, y) in opp_t:
            for dx, dy in neigh8:
                nx, ny = x + dx, y + dy
                if (nx, ny) in unclaimed:
                    opp_frontier.add((nx, ny))
    frontier = list(opp_frontier) if opp_frontier else []
    if not frontier:
        # Fallback: chase nearest unclaimed cell, else chase opponent to force flips.
        if unclaimed:
            frontier = list(unclaimed)
        else:
            frontier = [tuple(observation.get("opponent_position", (ox, oy)))]
    target = min(frontier, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))

    best = (0, 0)
    best_score = -10**18
    tx, ty = target
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        # Reward capturing (unclaimed or opponent) and moving closer to target.
        score = 0
        if (nx, ny) in opp_t:
            score += 50
        if (nx, ny) in unclaimed:
            score += 12
        if (nx, ny) in self_t:
            score += 0
        score += -2 * (abs(nx - tx) + abs(ny - ty))
        # Mild pressure: prefer reducing distance to opponent territory.
        if opp_t:
            # compute min manhattan to opponent territory cell (cheap, since grid small)
            md = 10**9
            for px, py in opp_t:
                d = abs(px - nx) + abs(py - ny)
                if d < md:
                    md = d
            score += -0.3 * md
        # Tie-break deterministically by lexicographic preference on (dx,dy)
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    # If all moves invalid, stay.
    if best_score == -10**18:
        return [0, 0]
    return [int(best[0]), int(best[1])]