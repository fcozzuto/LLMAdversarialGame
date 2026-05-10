def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set((x, y) for x, y in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    tr = int(observation.get("turns_remaining", 0))
    rem = int(observation.get("remaining_resource_count", len(resources)))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick best resource deterministically by "who can arrive first" + "urgency"
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources we can beat (arrive in <= turns and before opponent)
        lead = opd - myd  # positive good
        # Urgency: closer is better; if unreachable this turn-window, penalize heavily
        miss = 0 if myd <= tr else (myd - tr) * 20
        # If opponent is very close, deprioritize slightly to reduce being denied; when few resources remain, be bolder
        risk = 0 if lead >= 0 else (1 if rem <= 3 else 3) * (-lead)
        # Small tie-breaker: favor resources that are closer to us (break symmetry)
        key = (miss + risk, -lead, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Move to the adjacent cell (or stay) maximizing immediate advantage at the chosen target
    bestm = (0, 0)
    bestmk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        lead2 = opd2 - myd2
        miss2 = 0 if myd2 <= tr else (myd2 - tr) * 20
        # Prefer reducing distance to the target; also avoid stepping onto positions that let opponent "finish"
        # (opponent advantage increases when our distance grows relative to theirs)
        key = (miss2, -(lead2), myd2, nx, ny)
        if bestmk is None or key < bestmk:
            bestmk = key
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]