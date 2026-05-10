def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    opp_list = list(opp)
    tn = int(observation.get("turn_index", 0))
    cand = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue
        score = 0.0
        if (nx, ny) in unclaimed:
            score += 6.0
        if (nx, ny) in opp:
            score += 10.0
        if (nx, ny) in selft:
            score += 1.0
        # Move toward opponent territory / boundary adjacency
        if opp_list:
            dmin = 10**9
            for px, py in opp_list:
                d = abs(px - nx) + abs(py - ny)
                if d < dmin: dmin = d
            score += (9.0 / (1 + dmin))  # higher when closer
        # Prefer increasing capture frontier: adjacency to opponent territory
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in opp:
                    adj += 1
        score += 2.0 * adj
        # Mild preference for expanding away from obstacles (deterministic)
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs:
                    near_obs += 1
        score -= 1.5 * near_obs
        # Deterministic tie-breaker
        score += 0.001 * (((nx + 1) * 31 + (ny + 1) * 17 + tn) % 1000)
        cand.append((score, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    return [int(cand[0][1]), int(cand[0][2])]