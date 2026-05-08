def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    i_am_evader = ("evader" in self_role) or ("pursuer" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_spread(x, y):
        return max(abs(x - cx) + abs(y - cy) for cx, cy in corners)

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = dist2(nx, ny)
        # Penalize being "boxed in" by obstacles to avoid getting stuck by zigzag.
        neigh_block = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if not inb(tx, ty) or (tx, ty) in obs:
                neigh_block += 1
        if i_am_evader:
            val = d + 0.15 * corner_spread(nx, ny) - 0.05 * neigh_block
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < best)
        else:
            val = -d - 0.15 * corner_spread(nx, ny) - 0.05 * neigh_block
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < best)
        if better:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]