def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def clamp_to_free(nx, ny, x0, y0):
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return nx, ny
        return x0, y0

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0

    # Choose a "deny" target deterministically: maximize (opp-self) then closeness, slight center bias
    best_target = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # prefer where opponent is closer than us, but also reachable (avoid extremely far targets)
        sc = (od - sd) * 10 - sd
        sc += -(((rx - cx0) * (rx - cx0) + (ry - cy0) * (ry - cy0)) * 1e-4)
        cand = (sc, -od, -sd, rx, ry)
        if best_target is None or cand > best_target:
            best_target = cand
    tx, ty = best_target[3], best_target[4]

    # Evaluate each move by how much it denies opponent reaching (and also how much we progress)
    best_move = None
    for dx, dy in moves:
        nsx, nsy = clamp_to_free(sx + dx, sy + dy, sx, sy)
        # Denial heuristic: after our move, opponent-to-target minus our-to-target
        d_self = man(nsx, nsy, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        # Also consider keeping line toward other nearby resources if denial tie
        # (small bonus for reducing our distance to the closest resource too)
        best_min_self = None
        for rx, ry in resources:
            d = man(nsx, nsy, rx, ry)
            if (rx, ry) != (tx, ty) or True:
                if best_min_self is None or d < best_min_self:
                    best_min_self = d
        # obstacle-aware tie breakers: prefer not to step (stay) only if equally good
        moved = 1 if (nsx != sx or nsy != sy) else 0
        val = (d_opp - d_self) * 100 - d_self * 2 + moved
        # lexicographic deterministic tie break
        cand = (val, -(d_opp - d_self), -d_self, -best_min_self, dx, dy)
        if best_move is None or cand > best_move:
            best_move = cand
    return [int(best_move[4]), int(best_move[5])]