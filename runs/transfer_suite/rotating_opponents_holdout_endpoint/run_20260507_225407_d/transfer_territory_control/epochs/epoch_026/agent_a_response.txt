def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    opp_terr = observation.get("opponent_territory") or []
    opposet = set((int(p[0]), int(p[1])) for p in opp_terr if p and len(p) >= 2)

    unclaimed = observation.get("unclaimed_cells") or []
    unq = [(int(p[0]), int(p[1])) for p in unclaimed if p and len(p) >= 2]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer immediate flip if possible
    best_flip = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if (nx, ny) in opposet:
            best_flip = [dx, dy]
            break
    if best_flip is not None:
        return best_flip

    # Target selection: unclaimed cells adjacent to opponent territory; otherwise nearest unclaimed.
    opp_adj = set()
    for ox, oy in opposet:
        for dx, dy in dirs:
            ax, ay = ox + dx, oy + dy
            if inb(ax, ay) and (ax, ay) not in obs:
                opp_adj.add((ax, ay))
    opp_adj_unq = [c for c in unq if c in opp_adj]
    targets = opp_adj_unq if opp_adj_unq else unq

    # If no unclaimed, just move away from opponent (center-claim behavior) while staying safe.
    if not targets:
        tx, ty = w // 2, h // 2
        best = None
        best_sc = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            sc = dist((nx, ny), (tx, ty))
            if sc > best_sc:
                best_sc = sc
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Evaluate each move deterministically
    best_move = (0, 0)
    best_score = -10**9
    # Tie-break uses (score, -min_dist, dx, dy) with fixed order from dirs
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if (nx, ny) in opposet:
            sc = 10**6  # shouldn't happen due to flip check, but keep strong preference
        else:
            dmin = min(dist((nx, ny), t) for t in targets)
            sc = -dmin
            # Slightly prefer moves that step into unclaimed area adjacent to opponent (frontier)
            if (nx, ny) in opp_adj:
                sc += 0.5
        if sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]