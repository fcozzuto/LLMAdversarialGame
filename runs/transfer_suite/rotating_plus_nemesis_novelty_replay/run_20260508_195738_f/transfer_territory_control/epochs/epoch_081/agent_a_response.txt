def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opppos = observation.get("opponent_position", [0, 0])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_to_set(nx, ny, s):
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx or ddy:
                    if (nx + ddx, ny + ddy) in s:
                        return True
        return False

    # Build frontier targets: unclaimed adjacent to our territory
    frontier = []
    for ux, uy in unclaimed:
        if adj_to_set(ux, uy, selft):
            frontier.append((ux, uy))
    # Fallback: unclaimed adjacent to opponent territory (deny/contend)
    deny = []
    if not frontier:
        for ux, uy in unclaimed:
            if adj_to_set(ux, uy, opp):
                deny.append((ux, uy))

    # Decide whether we should press opponent or expand
    self_count = int(observation.get("self_territory_count", 0))
    opp_count = int(observation.get("opponent_territory_count", 0))
    press = (opp_count >= self_count)

    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # High priority: enter opponent territory (flip)
        if (nx, ny) in opp:
            score = 10**6
            # Slightly prefer moves that are closer to opponent's position
            score -= abs(nx - opppos[0]) + abs(ny - opppos[1])
            if score > best_score:
                best_score, best = score, [dx, dy]
            continue

        # Prefer moves that reduce distance to best target
        targets = frontier if (frontier and not press) else (frontier or deny or list(unclaimed)[:])
        if targets:
            # Deterministic: compute minimal manhattan and also whether we are stepping toward adjacency
            mind = 10**9
            near_adj = 0
            for tx, ty in targets:
                d = abs(tx - nx) + abs(ty - ny)
                if d < mind:
                    mind = d
            near_adj = 1 if adj_to_set(nx, ny, selft) else 0
            # Also reward closing in to unclaimed; discourage wandering far from our frontier
            score = 2000 * near_adj - 20 * mind
            # Edge pressure: keep collecting border cells
            score += 3 * (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1)
        else:
            # No targets: keep moving toward opponent position to avoid stalling
            score = - (abs(nx - opppos[0]) + abs(ny - opppos[1]))

        # Micro-preference for staying within unclaimed/expansion line
        if (nx, ny) in unclaimed:
            score += 150

        # Deterministic tie-break: prefer lexicographically smaller move among equals
        if score > best_score or (score == best_score and (best is None or [dx, dy] < best)):
            best_score, best = score, [dx, dy]

    return best if best is not None else [0, 0]