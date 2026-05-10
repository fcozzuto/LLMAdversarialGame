def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"][0], observation["self_position"][1]
    ox, oy = observation["opponent_position"][0], observation["opponent_position"][1]
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    self_role = observation.get("self_role", "")
    role_l = self_role.lower()
    is_pursuer = ("pursuer" in role_l) or ("chaser" in role_l) or ("hunter" in role_l)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    if is_pursuer:
        best_key = None
        best_move = (0, 0)
        for dx, dy, nx, ny in valid:
            cap = 1 if (nx == ox and ny == oy) else 0
            d = dist2(nx, ny, ox, oy)
            key = (-cap, d, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]
    else:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        target = corners[0]
        best_corner = -1
        for cx, cy in corners:
            dc = dist2(cx, cy, ox, oy)
            if dc > best_corner:
                best_corner = dc
                target = (cx, cy)
        tx, ty = target

        best_key = None
        best_move = (0, 0)
        for dx, dy, nx, ny in valid:
            d_away = dist2(nx, ny, ox, oy)
            d_corner = dist2(nx, ny, tx, ty)
            cap_pen = -1 if (nx == ox and ny == oy) else 0
            key = (-d_away, d_corner, cap_pen, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]