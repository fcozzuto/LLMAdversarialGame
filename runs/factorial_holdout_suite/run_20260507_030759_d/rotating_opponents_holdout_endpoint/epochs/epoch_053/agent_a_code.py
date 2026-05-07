def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # One-step lookahead: choose move that best improves capture race for a resource.
    # Tie-break: prefer closer resource after move.
    best_move = None
    best_val = None
    for dx, dy in legal:
        nsx, nsy = sx + dx, sy + dy
        move_val = None
        for rx, ry in resources:
            dself = man(nsx, nsy, rx, ry)
            dopp = man(ox, oy, rx, ry)
            # Advantage if we reach sooner; penalize being far.
            val = (dopp - dself) * 20 - dself
            # Slight preference for resources closer to center (reduces edge trapping).
            cx, cy = w // 2, h // 2
            val -= 0.3 * (abs(rx - cx) + abs(ry - cy)) * 0.0
            if move_val is None or val > move_val:
                move_val = val
        # If multiple moves pick same race advantage, pick one that reduces our distance to best target.
        # Compute quickly: use max over resources with same formula base.
        # (move_val already uses best resource, so recompute nearest distance to any resource that attains near-best.)
        nearest = min(man(nsx, nsy, rx, ry) for rx, ry in resources)
        val2 = move_val - 0.01 * nearest
        if best_val is None or val2 > best_val:
            best_val = val2
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]