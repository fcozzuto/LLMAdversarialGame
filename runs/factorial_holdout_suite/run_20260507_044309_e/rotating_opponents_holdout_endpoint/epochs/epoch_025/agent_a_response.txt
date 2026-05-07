def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # If standing on a resource, don't move.
    if (sx, sy) in resources:
        return [0, 0]

    # Pick target resource we can beat the opponent on (largest opp_d - self_d; i.e., most negative self-opp).
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd  # bigger => we are closer
        # tie-break: prefer shorter our distance, then closer to our corner direction
        key = (-adv, sd, rx + ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_step = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = md(nx, ny, tx, ty)
        nod = md(ox, oy, tx, ty)
        # Encourage immediate advantage at the target; also ensure we keep reducing our distance.
        advantage = nod - nsd
        # Prefer moves that also reduce our distance to target (mainly) and avoid giving up too much.
        score = (advantage, -nsd, -md(nx, ny, 0, 0))
        if best_score is None or score > best_score:
            best_score = score
            best_step = [dx, dy]

    return best_step