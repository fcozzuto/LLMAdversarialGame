def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))
    role = (observation.get("self_role", "") or "").lower()
    self_is_pursuer = ("purs" in role) or (role == "")
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in oset

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_score(x, y):
        d = [abs(x - cx) + abs(y - cy) for cx, cy in corners]
        return max(d), min(d)

    best_move = (0, 0)
    if self_is_pursuer:
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist(nx, ny, ox, oy)
            maxc, minc = corner_score(nx, ny)
            # minimize distance; tie-break: prefer heading away from nearest wall/corner constraints
            val = (d, -maxc, minc, dx, dy)
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        # Evader: maximize distance; tie-break: steer toward farthest corner and away from obstacles locally
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist(nx, ny, ox, oy)
            maxc, minc = corner_score(nx, ny)
            adj_obs = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in oset:
                    adj_obs += 1
            # maximize distance; then maximize farthest corner; then minimize obstacle adjacency
            val = (-d, -maxc, adj_obs, minc, dx, dy)
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]