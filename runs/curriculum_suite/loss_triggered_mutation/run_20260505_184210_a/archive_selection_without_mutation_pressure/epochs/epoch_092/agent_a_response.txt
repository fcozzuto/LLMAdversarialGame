def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        # Deterministic: move toward opponent while keeping within grid (and away from obstacles via inside()).
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    # Pick a target resource where we are relatively closer than opponent (maximize advantage).
    best_t = None
    best_key = None  # (my_dist - opp_dist, my_dist, -opp_dist)
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        key = (myd - opd, myd, -opd)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    best_move = None
    best_score = None
    # Score: prioritize reducing distance to target; if tie, increase opponent distance (deny).
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        myd2 = dist(nx, ny, rx, ry)
        opd2 = dist(nx + (ox - nx), ny + (oy - ny), ox, oy)  # simplifies to dist between (nx,ny) and (ox,oy)
        opd2 = dist(ox, oy, nx, ny)
        # Secondary: prefer moves that also reduce my distance to opponent only if no advantage? keep simple.
        score = (myd2, -opd2, abs((nx - ox)) + abs((ny - oy)))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]