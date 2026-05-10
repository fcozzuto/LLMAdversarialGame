def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = list(observation.get("unclaimed_cells", []) or [])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def neigh(adjx, adjy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = adjx + dx, adjy + dy
                    if inb(nx, ny):
                        yield nx, ny

    # Prefer unclaimed cells adjacent to opponent territory (deny counterclaims / take flips)
    adj_targets = []
    for ux, uy in unclaimed:
        for nx, ny in neigh(ux, uy):
            if (nx, ny) in opp:
                adj_targets.append((ux, uy))
                break

    targets = adj_targets if adj_targets else unclaimed
    if not targets:
        # If no unclaimed, drift toward opponent territory cells' neighborhood
        if opp:
            tx, ty = min(opp, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
        else:
            return [0, 0]
    else:
        # Deterministic closest choice
        tx, ty = min(targets, key=lambda p: (abs(p[0] - x) + abs(p[1] - y), p[0], p[1]))

    # Choose best move among legal neighbors; bias toward blocking adj_targets
    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        # small penalty for getting too close to opponent territory unless target is adjacent to it
        opp_dist = 10**6
        if opp:
            # compute min manhattan to opponent territory cheaply by sampling neighborhood if possible
            for ox, oy in opp:
                d = abs(ox - nx) + abs(oy - ny)
                if d < opp_dist:
                    opp_dist = d
                    if opp_dist == 0:
                        break
        score = dist
        if (tx, ty) in adj_targets:
            score -= 0.15 * opp_dist  # being closer to opponent is okay when target is a denial cell
        else:
            score += 0.08 * (8 - min(opp_dist, 8))  # avoid the opponent if we just chase generic unclaimed
        # mild obstacle proximity penalty
        near_obs = 0
        for px, py in neigh(nx, ny):
            if (px, py) in obs:
                near_obs += 1
        score += 0.2 * near_obs
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]