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

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy] if inside(sx + dx, sy + dy) else [0, 0]

    # Choose a target resource that is good for us but not immediately best for opponent.
    best_target = resources[0]
    best_tval = None
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # Prefer resources where we are closer; if tied, prefer where opponent is farther.
        tval = ds - 0.9 * do
        if best_tval is None or tval < best_tval or (tval == best_tval and (rx, ry) < best_target):
            best_tval = tval
            best_target = (rx, ry)

    rx, ry = best_target

    # For this turn, move to maximize a composite "secure score".
    # Self should get closer to target; also discourage moves that let opponent get closer too quickly.
    best_move = (0, 0)
    best_val = None
    for dx, dy, nx, ny in legal:
        dself = manh(nx, ny, rx, ry)
        dopp = manh(ox, oy, rx, ry)
        # Opponent likely heads toward its nearest resource; approximate by how much we reduce their access.
        # If we move closer to their position, it's bad; if we move away, it's good.
        opp_chase = -manh(nx, ny, ox, oy)
        # Avoid being "stepped over": penalize moves that reduce distance for opponent to our target too much.
        # (More reduction for opponent is estimated by comparing distances from their current position.)
        opp_reach_bonus = -0.3 * (dopp - manh(ox, oy, rx, ry))
        val = (-dself) + 0.25 * opp_chase + opp_reach_bonus

        # Deterministic tie-break: prefer lower dx, then lower dy, then staying only if equal.
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]