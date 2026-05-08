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
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in oset
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            if valid(x + dx, y + dy):
                c += 1
        return c
    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or (role == "")
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = md(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        if pursuer:
            corner_bias = max(md(nx, ny, cx, cy) for cx, cy in corners)
            val = (-dist, mob, corner_bias)
        else:
            # Evader: maximize distance; prefer high mobility and moving toward far corner from pursuer.
            far_corner = max((md(cx, cy, ox, oy) - md(nx, ny, cx, cy) * 0.1) for cx, cy in corners)
            val = (dist, mob, far_corner)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]