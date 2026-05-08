def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (nx, ny) == (sx, sy) or (inb(nx, ny) and (nx, ny) not in obs):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # If no resources, drift toward center corner-line to avoid deadlock near obstacles.
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            score = abs(nx - tx) + abs(ny - ty)
            if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]]

    # Choose resource maximizing advantage: (opp_distance - self_distance), tie-break by self distance.
    best_t = None
    best_key = None
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if not inb(rx, ry) or (rx, ry) in obs:
                continue
            sd = abs(rx - sx) + abs(ry - sy)
            od = abs(rx - ox) + abs(ry - oy)
            key = (od - sd, -sd, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best_t = (rx, ry)
    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    # One-step look: move that reduces distance to target, but also slightly discourages moving away from it.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = abs(nx - tx) + abs(ny - ty)
        # Secondary: prefer states that also reduce opponent's ability to be closer next turn.
        opp_d = abs(nx - ox) + abs(ny - oy)
        key = (d, opp_d, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]]