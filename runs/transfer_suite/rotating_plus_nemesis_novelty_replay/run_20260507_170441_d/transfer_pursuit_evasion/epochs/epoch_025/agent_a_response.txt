def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in role) or ("tag" in role) or ("hunter" in role)

    best_move = (0, 0)
    if pursuer:
        best_val = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            # Prefer reducing distance; mildly avoid edges/corners that might be worse after pursuit
            edge_pen = (1 if nx == 0 or nx == w - 1 else 0) + (1 if ny == 0 or ny == h - 1 else 0)
            corner_bias = max(dist2(nx, ny, cx, cy) for cx, cy in corners)
            val = d * 10 + edge_pen * 3 - corner_bias * 0.01
            if val < best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            corner_bias = max(dist2(nx, ny, cx, cy) for cx, cy in corners)
            edge_pen = (1 if nx == 0 or nx == w - 1 else 0) + (1 if ny == 0 or ny == h - 1 else 0)
            val = d * 10 + corner_bias * 0.5 - edge_pen * 2
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]