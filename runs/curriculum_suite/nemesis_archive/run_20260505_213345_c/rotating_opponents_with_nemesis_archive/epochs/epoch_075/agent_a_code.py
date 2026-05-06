def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist8(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    my_pos = (sx, sy)
    op_pos = (ox, oy)

    # Prefer resources we can reach sooner, especially those the opponent is not already close to.
    best_r = None
    best_val = None
    for r in resources:
        md = dist8(my_pos, r)
        od = dist8(op_pos, r)
        # Minimize: (my_dist) - 0.9*(opp_dist advantage against us)
        # i.e., prioritize large od-md (opponent farther than us) while keeping md low.
        val = md - 0.9 * od
        if best_val is None or val < best_val or (val == best_val and r < best_r):
            best_val = val
            best_r = r

    tx, ty = best_r
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Deterministic fallback: try axis move toward target (diagonal blocked).
        if dx != 0 and (sx + dx, sy) not in obstacles:
            return [dx, 0]
        if dy != 0 and (sx, sy + dy) not in obstacles:
            return [0, dy]
        # Last resort: stay (engine will reject invalid moves by staying).
        return [0, 0]

    return [dx, dy]