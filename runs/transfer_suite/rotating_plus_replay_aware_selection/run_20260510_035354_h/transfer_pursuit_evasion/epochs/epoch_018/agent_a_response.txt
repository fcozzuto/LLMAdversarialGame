def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    def role_is_purs(role):
        r = (role or "").lower()
        if "purs" in r:
            return True
        if "evad" in r:
            return False
        return None

    sr = role_is_purs(observation.get("self_role"))
    orr = role_is_purs(observation.get("opponent_role"))
    if sr is None:
        sr = (orr is False)
    pursuer = bool(sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def manhattan(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def corner_score(x, y):
        # pursuer: move toward closest corner of opponent; evader: toward farthest
        vals = [manhattan(x, y, c[0], c[1]) for c in corners]
        return min(vals) if pursuer else max(vals)

    best_val = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = manhattan(nx, ny, ox, oy)
        d_corner = corner_score(nx, ny)

        # Obstacle avoidance: strong penalty near obstacles, mild reward for moving away
        rep = 0
        for (bx, by) in obs:
            dist = abs(nx - bx) + abs(ny - by)
            if dist == 0:
                rep += 10**6
            elif dist == 1:
                rep += 250
            elif dist == 2:
                rep += 60
            elif dist == 3:
                rep += 15
            else:
                rep += 0

        # Wall-run evasion/pursuit: prefer lateral moves when pursuing, and prefer breaking line when evading
        line_x = 1 if nx == ox else 0
        line_y = 1 if ny == oy else 0
        line_pen = (line_x + line_y) * 8

        if pursuer:
            val = (-d_opp) + 0.12 * d_corner - rep - line_pen
        else:
            val = (d_opp) + 0.18 * d_corner - rep - line_pen

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move