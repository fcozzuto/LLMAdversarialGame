def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def kingdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = None

    # Deterministic small lookahead: choose move that maximizes our "lead quality"
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        best_target_key = None
        for tx, ty in resources:
            our_t = kingdist(nx, ny, tx, ty)
            opp_t = kingdist(ox, oy, tx, ty)
            lead = opp_t - our_t  # positive => we arrive earlier
            # Prefer guaranteed lead, then larger lead, then closer to speed up ties
            key = (0 if lead > 0 else 1, -lead, our_t, tx, ty)
            if best_target_key is None or key < best_target_key:
                best_target_key = key
        # Penalize moving closer to obstacles (soft avoidance)
        min_obs = 10
        for (bx, by) in obstacles:
            d = kingdist(nx, ny, bx, by)
            if d < min_obs: min_obs = d
        obs_pen = -0.2 * min_obs  # higher min_obs => less negative
        val = (best_target_key[0], best_target_key[1], best_target_key[2], obs_pen, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx if (sx + dx, sy + dy) != (sx, sy) else 0 if dx == 0 else dx, dy if (sx + dx, sy + dy) != (sx, sy) else 0 if dy == 0 else dy)

    return [int(best_move[0]), int(best_move[1])]