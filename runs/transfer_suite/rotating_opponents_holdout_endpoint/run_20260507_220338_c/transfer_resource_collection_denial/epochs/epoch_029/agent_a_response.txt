def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_key_from(posx, posy):
        best_k = None
        best_r = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = manh(posx, posy, rx, ry)
            opd = manh(ox, oy, rx, ry)
            # Prefer resources where we are closer; then prefer near/contested; then prefer lower coordinate sum.
            k = (opd - myd, -(myd + opd), -(rx + ry))
            if best_k is None or k > best_k:
                best_k = k
                best_r = (rx, ry)
        if best_r is None:
            return (resources[0], 0)
        return best_r, best_k

    target, _ = best_key_from(sx, sy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Evaluate by re-targeting from the candidate position.
        (tr, _) = best_key_from(nx, ny)
        myd = manh(nx, ny, tr[0], tr[1])
        opd = manh(ox, oy, tr[0], tr[1])
        k = (opd - myd, -(myd + opd), -(tr[0] + tr[1]), -manh(nx, ny, sx, sy))
        if best_score is None or k > best_score:
            best_score = k
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]