def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("pursuer" in str(observation.get("opponent_role", "")).lower())

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def edge_pot(x, y):
        dx = x - cx
        dy = y - cy
        return dx * dx + dy * dy

    dx_t = 0 if ox == sx else (1 if ox > sx else -1)
    dy_t = 0 if oy == sy else (1 if oy > sy else -1)
    pref = [(dx_t, dy_t), (dx_t, 0), (0, dy_t), (dx_t, -dy_t), (-dx_t, dy_t), (-dx_t, -dy_t), (-dx_t, 0), (0, -dy_t), (0, 0)]

    best_val = None
    best_move = (0, 0)
    for m in pref:
        mdx, mdy = m
        nx, ny = sx + mdx, sy + mdy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        if pursuer:
            # Primary: minimize distance. Secondary: move toward edges/corners to corner evader.
            val = (d, -edge_pot(nx, ny))
        else:
            # Primary: maximize distance. Secondary: stay near center to avoid being herded into corners/walls.
            val = (-d, edge_pot(nx, ny))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (mdx, mdy)

    if ok(sx, sy):
        return [int(best_move[0]), int(best_move[1])]
    return [0, 0]