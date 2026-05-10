def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = moves

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def best_target_value(px, py):
        best = None
        for rx, ry in resources:
            if (px, py) == (rx, ry):
                val = (10**9, -manh(px, py, ox, oy), 0, rx, ry)
            else:
                self_d = manh(px, py, rx, ry)
                opp_d = manh(ox, oy, rx, ry)
                # Prefer resources where we are closer than opponent; tie-break by urgency.
                val = (opp_d - self_d, -self_d, self_d, rx, ry)
            if best is None or val > best:
                best = val
        return best

    # Depth-2 lookahead: pick move maximizing current advantage, then next advantage.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        v1 = best_target_value(nx, ny)
        # Second step: assume opponent stays (deterministic) and we optimize locally.
        best_v2 = None
        for ddx, ddy in dirs:
            nnx, nny = nx + ddx, ny + ddy
            if not (0 <= nnx < w and 0 <= nny < h) or (nnx, nny) in obs:
                continue
            v2 = best_target_value(nnx, nny)
            if best_v2 is None or v2 > best_v2:
                best_v2 = v2

        score = (v1, best_v2)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move == (0, 0):
        # Fallback: greedy move toward best target
        target = max(resources, key=lambda r: (manh(ox, oy, r[0], r[1]) - manh(sx, sy, r[0], r[1]), -manh(sx, sy, r[0], r[1])))
        tx, ty = target
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]
    return [best_move[0], best_move[1]]