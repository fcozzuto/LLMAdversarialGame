def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # Race-driven interception: choose move that maximizes our best "race margin" next turn.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Primary: maximize (opp_d - our_d_next) over resources.
        # Secondary: minimize our_d_next for the best resource.
        cur_best_margin = None
        cur_best_d = None
        for rx, ry in resources:
            our_d = man((nx, ny), (rx, ry))
            opp_d = man((ox, oy), (rx, ry))
            margin = opp_d - our_d
            if cur_best_margin is None or margin > cur_best_margin or (margin == cur_best_margin and our_d < cur_best_d):
                cur_best_margin, cur_best_d = margin, our_d
        # Small tie-breakers to reduce dithering: prefer moves that lower our distance to that chosen target.
        # Also discourage moving away from opponent when we already lead less.
        lead_score = cur_best_margin
        opp_step = man((nx, ny), (ox, oy))
        key = (lead_score, -cur_best_d, -opp_step, -dx, -dy)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]