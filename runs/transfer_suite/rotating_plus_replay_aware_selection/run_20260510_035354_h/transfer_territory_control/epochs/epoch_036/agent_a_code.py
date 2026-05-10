def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles if inb(x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []

    my_set = set((x, y) for x, y in my_t if inb(x, y))
    op_set = set((x, y) for x, y in op_t if inb(x, y))
    un_set = set((x, y) for x, y in unclaimed if inb(x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist2(p, q):
        dx = p[0] - q[0]
        dy = p[1] - q[1]
        return dx * dx + dy * dy

    # Target selection: prefer nearest unclaimed; else nearest opponent territory.
    if un_set:
        target_pool = list(un_set)
    elif op_set:
        target_pool = list(op_set)
    else:
        target_pool = [(ax, ay)]
    target_pool.sort(key=lambda p: (dist2((ax, ay), p), p[0], p[1]))
    # Also consider frontier-like unclaimed/opponent-adjacent cells (deterministic cap).
    frontier = []
    for x, y in target_pool[:24]:
        if (x, y) in un_set:
            frontier.append((x, y))
        else:
            frontier.append((x, y))
    target = frontier[0] if frontier else (ax, ay)

    best = (0, 0)
    best_score = -10**18
    my_d = dist2((ax, ay), target)
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        p = (nx, ny)

        score = 0
        d = dist2(p, target)
        score += 60 * (my_d - d > 0) + 8 * (my_d - d)  # move closer strongly

        if p in un_set:
            score += 220
        if p in op_set:
            score += 80
        if p in my_set:
            score += 15

        # Avoid stepping into "unsafe" corners when chasing unclaimed:
        # if p is adjacent to obstacles, slightly reduce to prevent getting stuck.
        adj_obs = 0
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            q = (nx + ox, ny + oy)
            if (q[0], q[1]) in obs:
                adj_obs += 1
        score -= 10 * adj_obs

        # Small deterministic bias toward diagonal when scores tie.
        score += 1 if (dx != 0 and dy != 0) else 0

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]