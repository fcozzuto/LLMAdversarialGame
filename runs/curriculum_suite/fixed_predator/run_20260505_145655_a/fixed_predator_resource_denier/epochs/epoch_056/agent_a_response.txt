def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a target to "deny": prefer cells where we are closer than opponent, else still where we can close the gap.
    best_t = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        gap = od - sd  # positive means we are closer
        # Prefer positive gap; if none, prefer less distance and reducing opponent advantage.
        val = (gap * 10.0) - (sd * 0.35) - (od * 0.1)
        # Mild center bias
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        val += -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy)) * 0.0002
        if best_t is None or val > best_t[0]:
            best_t = (val, rx, ry, sd, od)
    _, tx, ty, _, _ = best_t

    # Evaluate possible moves with obstacle and board bounds.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    # Deterministic tie-breaking: sort by (-score, dist_to_target, dx, dy) so stable.
    ranked = []
    for dx, dy, nx, ny in moves:
        d_self = man(nx, ny, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        # Primary: increase our closeness relative to opponent for this target.
        deny = (d_opp - d_self)
        # Secondary: avoid drifting away from opponent's likely interference by slightly preferring smaller self distance.
        val = deny * 9.0 - d_self * 0.6
        # Very small preference for moving toward target direction if deny tie
        val += -0.0001 * (abs(nx - tx) + abs(ny - ty))
        ranked.append((-val, d_self, dx, dy))
    ranked.sort()
    dx, dy = ranked[0][2], ranked[0][3]
    return [int(dx), int(dy)]