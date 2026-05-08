def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    frontier = set()
    if unclaimed and opp_t:
        for ux, uy in unclaimed:
            for dx, dy in neighbors:
                if (ux + dx, uy + dy) in opp_t:
                    frontier.add((ux, uy))
                    break

    # Primary: grab cells adjacent to opponent territory (likely to flip quickly)
    # Secondary: closest unclaimed (prefer also closer to opponent side)
    if frontier:
        target = min(frontier, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), -abs(p[0] - ox) - abs(p[1] - oy), p[0], p[1]))
    elif unclaimed:
        target = min(unclaimed, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        # No unclaimed: advance to opponent if reachable, else hold
        target = (ox, oy)

    tx, ty = int(target[0]), int(target[1])
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        # Tie-break: prefer moves that step into opponent territory (flipping enabled) or own territory (stabilize)
        step_score = 0
        if (nx, ny) in opp_t:
            step_score -= 100
        if (nx, ny) in self_t:
            step_score += 5
        cand = (dist, step_score, dx, dy)
        if cand[0] < best[0] or (cand[0] == best[0] and (cand[1] < best[1])):
            best = cand
    dx, dy = best[2], best[3]
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]