def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for o in obs_list:
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
    is_pursuer = ("purs" in role) or ("tag" in role) or ("hunter" in role)

    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        corner_bias = max(dist2(nx, ny, cx, cy) for cx, cy in corners)  # evader prefers large
        # pursuer prefers smaller distance and slightly tighter movement toward opponent
        # evader prefers larger distance and slightly toward farthest corner
        if is_pursuer:
            # primary: minimize distance; secondary: prefer decreasing max axis difference
            axis = max(abs(nx - ox), abs(ny - oy))
            val = d * 1000 + axis * 10 - corner_bias * 0.01
            better = (best_val is None) or (val < best_val)
        else:
            axis = max(abs(nx - ox), abs(ny - oy))
            val = d * 1000 + axis * 10 + corner_bias
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best_move = [dx, dy]

    # If all moves blocked (unlikely), stay still
    return [int(best_move[0]), int(best_move[1])]