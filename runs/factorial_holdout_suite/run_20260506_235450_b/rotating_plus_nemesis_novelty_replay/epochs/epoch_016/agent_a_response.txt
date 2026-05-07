def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def best_step(tx, ty):
        best = None
        for mx, my in cand:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Prefer approaching target; add safety against being overtaken.
            k = (dist2(nx, ny, tx, ty),
                 abs(nx - ox) + abs(ny - oy),
                 dist2(nx, ny, ox, oy))
            if best is None or k < best:
                best = k
                best_move = [mx, my]
        return best_move if best is not None else [0, 0]

    # Choose a target resource, prioritizing ones we can reach (or at least threaten) first.
    if resources:
        scored = []
        for rx, ry in resources:
            ds = dist2(sx, sy, rx, ry)
            do = dist2(ox, oy, rx, ry)
            # Threat-first: if we are closer than opponent, boost strongly.
            gap = do - ds
            scored.append((-(1 if gap > 0 else 0) * 10000 + (-gap), ds, rx, ry))
        _, _, tx, ty = min(scored)
        return best_step(tx, ty)

    # No resources left: endgame, move to corner farthest from opponent.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda p: (dist2(p[0], p[1], ox, oy), -dist2(sx, sy, p[0], p[1])))
    return best_step(tx, ty)