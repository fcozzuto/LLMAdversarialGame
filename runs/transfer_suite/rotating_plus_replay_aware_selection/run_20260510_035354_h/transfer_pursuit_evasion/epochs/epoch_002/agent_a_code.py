def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer_like = ("purs" in self_role) or (self_role == "pursuer") or ("evad" in opp_role and "purs" in self_role) or ("evad" in self_role and "purs" in opp_role)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def edge_pen(x, y):
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    best = None
    best_val = None

    if pursuer_like:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d2 = dist2(nx, ny, ox, oy)
            center2 = dist2(nx, ny, cx, cy)
            val = (d2, center2, -edge_pen(nx, ny), dx, dy)
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)
    else:
        # evade: maximize distance; also drift toward farthest corner deterministically
        corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
        target_corner = max(corners, key=lambda c: abs(c[0]-ox) + abs(c[1]-oy))
        tx, ty = target_corner
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d2 = dist2(nx, ny, ox, oy)
            to_corner = dist2(nx, ny, tx, ty)
            center2 = dist2(nx, ny, cx, cy)
            val = (-d2, -to_corner, center2, -edge_pen(nx, ny), dx, dy)
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]