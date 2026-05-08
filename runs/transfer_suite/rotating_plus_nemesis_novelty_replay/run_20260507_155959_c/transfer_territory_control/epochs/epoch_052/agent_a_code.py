def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)

    # Preferred targets: unclaimed near us, else unclaimed closest to opponent (to contest their center-claim), else any unclaimed.
    if unclaimed:
        center = (w // 2, h // 2)
        prefer_opp = (len(opp_t) > len(self_t))
        items = list(unclaimed)
        if prefer_opp:
            tx, ty = min(items, key=lambda t: (abs(t[0] - center[0]) + abs(t[1] - center[1]), abs(t[0] - sx) + abs(t[1] - sy)))[0:2]
        else:
            tx, ty = min(items, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), abs(t[0] - (w // 2)) + abs(t[1] - (h // 2))))[0:2]
    else:
        # No unclaimed: try to approach opponent territory or just move toward center.
        tx, ty = (w // 2, h // 2)

    dirs = [(0,0),(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]
    best_move = [0, 0]
    best_score = -10**9
    # Determine if we are adjacent to any opponent cell (high priority to flip).
    adj_opp = False
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in opp_t:
            adj_opp = True
            break

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = 0
        if (nx, ny) in opp_t:
            score += 5000
        if (nx, ny) in unclaimed:
            score += 2000
        if (nx, ny) in self_t:
            score += 150
        # Move guidance: toward chosen target, but avoid stepping into opponent territory only when it would be worse than grabbing unclaimed.
        dist_target = abs(nx - tx) + abs(ny - ty)
        score += 200 - 20 * dist_target
        # If adjacent to opponent, prefer moves that immediately reduce distance to them.
        if adj_opp:
            score += 30 - 10 * min(abs(nx - x) + abs(ny - y) for (x, y) in (opp_t or [(ox, oy)]))
        # Soft repel from obstacles (discourage moves that are adjacent to many obstacles).
        around_obs = 0
        for ex, ey in dirs:
            ax, ay = nx + ex, ny + ey
            if inb(ax, ay) and (ax, ay) in obs:
                around_obs += 1
        score -= 5 * around_obs
        # Deterministic tie-break: lexicographically smallest move among best scores.
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move