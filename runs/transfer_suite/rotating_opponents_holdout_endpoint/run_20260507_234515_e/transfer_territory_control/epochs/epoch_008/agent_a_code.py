def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbors(x, y):
        for dx, dy in dirs:
            if dx == 0 and dy == 0: 
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    # Prefer to expand from our frontier into unclaimed (territory-edge claiming behavior correction)
    frontier_targets = []
    for cx, cy in self_terr:
        for nx, ny in neighbors(cx, cy):
            if (nx, ny) in obs: 
                continue
            if (nx, ny) in unclaimed:
                frontier_targets.append((nx, ny))

    # If no frontier, pressure by moving toward opponent territory boundaries
    pressure_targets = []
    if not frontier_targets:
        for ox, oy in opp_terr:
            for nx, ny in neighbors(ox, oy):
                if (nx, ny) in obs:
                    continue
                if (nx, ny) not in self_terr:
                    if (nx, ny) in unclaimed or (nx, ny) in opp_terr:
                        pressure_targets.append((nx, ny))

    targets = frontier_targets if frontier_targets else (pressure_targets if pressure_targets else list(unclaimed))
    if not targets:
        return [0, 0]

    # Rank targets: closest, then prefer unclaimed (more growth), then prefer those adjacent to opponent
    def target_score(t):
        base = dist((sx, sy), t)
        is_un = 0 if t in unclaimed else 50
        adj_opp = 0
        for nx, ny in neighbors(t[0], t[1]):
            if (nx, ny) in opp_terr:
                adj_opp = -3
                break
        return (base + is_un + adj_opp, t[0], t[1])

    target = min(targets, key=target_score)

    # Choose the step that deterministically reduces distance to the target while avoiding obstacles
    best = (10**9, 10**9, (0, 0))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = dist((nx, ny), target)
        # Small bonus for entering opponent-owned (flipping on entry)
        flip_bonus = -6 if (nx, ny) in opp_terr else 0
        # Avoid oscillation against our own territory interior: slight penalty if staying far from frontier when possible
        stay_bonus = 0 if (dx == 0 and dy == 0) else 0
        val = (d + (-flip_bonus), abs(nx - sx) + abs(ny - sy) + stay_bonus, dx, dy)
        # lexicographic with additional tie-break to be deterministic
        if val < (best[0], best[1], best[2][0], best[2][1]):
            best = (val[0], val[1], (dx, dy))

    return [int(best[2][0]), int(best[2][1])]