def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = str(observation.get("self_role", "") or "").lower()
    evader = "evader" in self_role

    obs_set = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def free_moves(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    # Target corner differs from the incumbent: for evader, use the corner opposite to opponent.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    if evader:
        tx, ty = w - 1 - best_corner[0], h - 1 - best_corner[1]
    else:
        tx, ty = best_corner

    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = dist2(nx, ny)
        d_tgt = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        fm = free_moves(nx, ny)

        # Avoid getting closer to opponent when evading; keep escape corridor.
        if evader:
            # Primary: maximize distance from opponent; Secondary: approach target corner; Tertiary: mobility.
            val = (d_opp, -d_tgt, fm)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            # Primary: minimize distance to opponent; Secondary: reduce target distance; Tertiary: mobility.
            val = (-d_opp, -d_tgt, fm)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]