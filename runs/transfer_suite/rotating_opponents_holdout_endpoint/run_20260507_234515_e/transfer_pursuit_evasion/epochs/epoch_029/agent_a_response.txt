def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("direct" in role and "evad" not in role) or (not role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def d2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: (c[0] - ox) ** 2 + (c[1] - oy) ** 2)

    curd = d2(sx, sy)
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in oset:
            continue

        nd = d2(nx, ny)
        if is_pursuer:
            # Primary: get closer. Tie: avoid increasing or staying. Tie: prefer non-blocked direction.
            stay_pen = 1 if (dx == 0 and dy == 0) else 0
            inc_pen = 0 if nd <= curd else 1
            val = ( -nd, inc_pen, stay_pen, (nx, ny) )
        else:
            # Evader: maximize distance and drift toward farthest corner from opponent.
            corner_dx = nx - target_corner[0]
            corner_dy = ny - target_corner[1]
            corner_dist2 = corner_dx * corner_dx + corner_dy * corner_dy
            # maximize distance, then minimize corner distance
            stay_pen = 1 if (dx == 0 and dy == 0) else 0
            val = ( nd, -corner_dist2, -(-stay_pen), (nx, ny) )

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]