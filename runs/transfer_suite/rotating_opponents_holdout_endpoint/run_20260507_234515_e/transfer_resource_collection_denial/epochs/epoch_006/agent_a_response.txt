def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
    moves.append((0, 0))
    # deterministic ordering: closer to straight toward positive axes first, then stay
    moves.sort(key=lambda m: (m == (0, 0), -m[0], -m[1], m[0], m[1]))

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    if not resources:
        return [0, 0]

    # Choose a target resource where we are currently leading, with a small preference for being closer.
    best_r = None
    best_tscore = None
    for rx, ry in resources:
        sd = dist2(sx, sy, rx, ry)
        od = dist2(ox, oy, rx, ry)
        lead = od - sd  # positive means we are closer than opponent
        tscore = lead * 1000000 - sd  # strong lead preference; tie-break by being closer
        if best_tscore is None or tscore > best_tscore:
            best_tscore = tscore
            best_r = (rx, ry)

    rx, ry = best_r

    # Evaluate legal next moves by (1) improving our distance to target,
    # (2) reducing opponent's distance to target relative to ours,
    # (3) penalizing being blocked by local obstacles indirectly via legal moves only.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = dist2(nx, ny, rx, ry)
        no = dist2(ox, oy, rx, ry)
        # Advantage after move: we want ns to be small vs no; also prefer not to worsen current lead.
        adv_after = no - ns
        # Secondary: if we can reach some resource quickly, prefer it (opportunistic but deterministic)
        min_ns_any = None
        for ax, ay in resources:
            d = dist2(nx, ny, ax, ay)
            if min_ns_any is None or d < min_ns_any:
                min_ns_any = d
        # Higher is better
        val = adv_after * 1000000 - ns - (min_ns_any if min_ns_any is not None else 0) // 2
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]