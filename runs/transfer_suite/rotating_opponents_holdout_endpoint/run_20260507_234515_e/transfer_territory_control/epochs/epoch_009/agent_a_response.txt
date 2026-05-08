def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))
    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def mindist(points, x, y):
        best = 10**9
        for px, py in points:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    # Build frontier: unclaimed cells adjacent to our territory (including diagonals).
    frontier = []
    if self_terr:
        for cx, cy in self_terr:
            for dx, dy in dirs:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = cx + dx, cy + dy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    frontier.append((nx, ny))
        if frontier:
            frontier = list(set(frontier))

    targets = frontier if frontier else list(unclaimed) if unclaimed else []
    # Also consider stealing near opponent territory if we have none to expand into.
    if not targets and opp_terr:
        targets = list(opp_terr)

    if not targets:
        # Fallback: drift towards board center.
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        dx = 0 if sx == int(tx) else (1 if sx < int(tx) else -1)
        dy = 0 if sy == int(ty) else (1 if sy < int(ty) else -1)
        return [dx, dy]

    # Evaluate immediate move by local scoring.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        if (nx, ny) in opp_terr:
            # High value: capture by stepping into opponent territory (flipping enabled).
            score = 1200
        elif (nx, ny) in self_terr:
            # Staying on our territory is safe but less valuable.
            score = 60
        elif (nx, ny) in unclaimed:
            score = 250
        else:
            score = 30

        # Prefer moves that reduce distance to chosen targets.
        score -= 2 * mindist(targets, nx, ny)

        # Slightly bias away from obstacles to reduce collision chance.
        near_obs = 0
        for adx, ady in dirs:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) in obs:
                near_obs += 1
        score -= 15 * near_obs

        # Deterministic tie-break: prefer lower dx, then lower dy, then staying.
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]