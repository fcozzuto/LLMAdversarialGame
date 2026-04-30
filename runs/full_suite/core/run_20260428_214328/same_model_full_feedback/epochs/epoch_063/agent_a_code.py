def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose a target resource where we have a relative advantage over opponent.
    best_t = None
    best_t_adv = -10**18
    tiebreak = None
    for (rx, ry) in resources:
        myd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - myd  # positive means we are closer (in grid distance)
        tie = (rx, ry, myd)  # deterministic
        if adv > best_t_adv or (adv == best_t_adv and tie < tiebreak):
            best_t_adv = adv
            best_t = (rx, ry)
            tiebreak = tie

    # If no resources, just retreat/hold to avoid illegal.
    if best_t is None:
        return [0, 0]

    rx, ry = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Late game: weight increasing our distance from opponent more (deny captures)
    t = int(observation.get("turn_index") or 0)
    rem = int(observation.get("remaining_resource_count") or 0)
    late = 1 if (t > 45 or rem <= 6) else 0

    best = None
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd2 = man(nx, ny, rx, ry)
        od2 = man(ox, oy, rx, ry)
        # Also consider moving to increase our advantage margin and slightly keep away from opponent position.
        adv2 = od2 - myd2
        opp_spread = man(nx, ny, ox, oy)
        val = adv2 * 100 - myd2
        val += (opp_spread if late else 0)
        # Deterministic tie-break: prefer moves with smallest dx,dy lexicographically.
        if val > best_val:
            best_val = val
            best = (dx, dy)
        elif val == best_val and best is not None:
            if (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]