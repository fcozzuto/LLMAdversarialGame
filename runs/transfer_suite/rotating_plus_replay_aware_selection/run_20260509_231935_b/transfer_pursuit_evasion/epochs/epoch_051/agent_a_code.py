def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    if "evader" in self_role:
        evade = True
    elif "evader" in opp_role:
        evade = False
    else:
        # Default to pursuer if ambiguous
        evade = ("pursuer" in self_role) or ("hunter" in self_role)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def obstacle_clear(nx, ny):
        # Min distance to any obstacle (bigger is safer)
        md = 99
        for (x, y) in obs:
            d = abs(nx - x) + abs(ny - y)
            if d < md:
                md = d
                if md == 0:
                    break
        return md

    # If pursuer: reduce distance; if evader: increase distance, also bias toward farthest corner.
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if evade:
            far_corner = max(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
            # Encourage moving away and toward far corners; discourage tight obstacle proximity.
            val = (d2 * 10) + far_corner - (100 - obstacle_clear(nx, ny))
        else:
            # Encourage closing distance; discourage obstacle tightness and staying still when not best.
            stay_pen = 1 if (dx == 0 and dy == 0) else 0
            val = (-d2 * 10) - (100 - obstacle_clear(nx, ny)) - stay_pen

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move