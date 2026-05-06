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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        # deterministic drift toward opponent to contest space
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if inside(nx, ny) else [0, 0]

    # For each candidate move: maximize how many resources we become strictly closer to than opponent,
    # then minimize our distance to the best (closest) resource, with stable tie-breaker.
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        closer_count = 0
        min_my = 10**9
        min_opp = 10**9
        for rx, ry in resources:
            d_my = manh(nx, ny, rx, ry)
            d_opp = manh(ox, oy, rx, ry)
            if d_my < d_opp:
                closer_count += 1
            if d_my < min_my:
                min_my = d_my
            if d_opp < min_opp:
                min_opp = d_opp
        # Prefer denial (closer_count), then press a resource (min_my), then keep relative pressure (min_opp - min_my),
        # then bias toward moving toward opponent only if still tied.
        score = (closer_count, -min_my, -(min_opp - min_my), -manh(nx, ny, ox, oy), dx, dy)
        if best is None or score > best[0]:
            best = (score, [dx, dy])

    return best[1]