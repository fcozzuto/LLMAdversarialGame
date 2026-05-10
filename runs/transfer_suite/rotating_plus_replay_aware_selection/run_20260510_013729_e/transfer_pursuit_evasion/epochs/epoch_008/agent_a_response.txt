def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    ob = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ob.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    self_is_evader = "evader" in role

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in ob

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a deterministic target corner to steer toward/away from opponent
    # Evader: far from pursuer; Pursuer: near pursuer (so move toward the opponent-biased corner).
    scored_corners = []
    for cx, cy in corners:
        d_op = manh(cx, cy, ox, oy)
        d_me = manh(cx, cy, sx, sy)
        if self_is_evader:
            key = (d_op, -d_me)  # prefer corners far from opponent, then closer to me
        else:
            key = (-d_op, d_me)  # prefer corners near opponent, then closer to me
        scored_corners.append((key, (cx, cy)))
    target = max(scored_corners, key=lambda t: t[0])[1]

    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best_move = [0, 0]
    best_primary = None
    best_secondary = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_target = manh(nx, ny, target[0], target[1])
        d_opp = manh(nx, ny, ox, oy)
        mob = mobility(nx, ny)

        if self_is_evader:
            primary = (d_opp, d_target)      # maximize distance to opponent; also increase distance to target (corner)
            secondary = mob                 # then maximize mobility
        else:
            primary = (-d_opp, -d_target)   # minimize distance to opponent; also reduce distance to target
            secondary = mob                 # then maximize mobility

        if best_primary is None or primary > best_primary or (primary == best_primary and secondary > best_secondary):
            best_primary = primary
            best_secondary = secondary
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]