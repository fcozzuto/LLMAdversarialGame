def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    is_pursuer = ("purs" in self_role) or ("purs" in opp_role) or ("evader" not in self_role)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def nearest_obst_d2(x, y):
        best = 10**9
        for (px, py) in obstacles:
            d = dist2(x, y, px, py)
            if d < best:
                best = d
        return best if obstacles else best

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if is_pursuer:
            # Pursue: minimize distance; if tied, move to reduce opponent escaping routes (prefer closer to center)
            val = dist2(nx, ny, ox, oy)
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_pen = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            val = (val, center_pen)
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            # Evade: maximize distance; if threatened, prioritize furthest corner; avoid obstacles
            d = dist2(nx, ny, ox, oy)
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner_d = max(dist2(nx, ny, cx, cy) for (cx, cy) in corners)
            obst_d = nearest_obst_d2(nx, ny)
            threatened = dist2(sx, sy, ox, oy) <= 9  # close-range
            # Score tuple: larger is better; deterministic tie-break by corner distance then obstacle clearance
            val = (d + (far_corner_d if threatened else 0), far_corner_d, obst_d)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]