def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles if inb(x, y))
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    my_set = set((x, y) for x, y in my_t if inb(x, y))
    op_set = set((x, y) for x, y in op_t if inb(x, y))
    un_set = set((x, y) for x, y in unclaimed if inb(x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2, (h - 1) / 2

    best = None
    best_val = -10**18
    # Nearest unclaimed/opp cell for mild pathing without full search
    targets = list(un_set) if un_set else list(op_set)
    if not targets:
        target = (int(cx), int(cy))
    else:
        target = min(targets, key=lambda p: (p[0] - ax) * (p[0] - ax) + (p[1] - ay) * (p[1] - ay))

    tx, ty = target
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        val = 0
        # Prefer expanding territory
        if (nx, ny) in un_set:
            val += 60
        if (nx, ny) in op_set:
            val += 35  # flipping on entry
        if (nx, ny) in my_set:
            val += 8
        # Avoid edges unless it helps reach target
        edge_pen = min(nx, ny, (w - 1 - nx), (h - 1 - ny))
        val += edge_pen * 0.1
        # Goal direction
        dist_to_goal = abs(nx - tx) + abs(ny - ty)
        val += 20 / (1 + dist_to_goal)
        # Slightly prefer moving closer to center
        dist_center = abs(nx - cx) + abs(ny - cy)
        val += 2.0 / (1 + dist_center)
        # Deterministic tie-break: fixed move order by checking first
        if val > best_val:
            best_val = val
            best = [dx, dy]
    return best if best is not None else [0, 0]