def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer; otherwise prefer those far from opponent.
        key = (opd - myd, -myd, -(rx + ry), - (rx * 13 + ry * 7))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (int(rx), int(ry))

    tx, ty = best_t

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic priority for ties: prefer straight moves over diagonals, then x direction.
    priority = {(0, 0): 0, (0, -1): 1, (0, 1): 2, (1, 0): 3, (-1, 0): 4, (1, -1): 5, (-1, -1): 6, (1, 1): 7, (-1, 1): 8}

    best_m = (0, 0)
    best_mkey = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(nx, ny, ox, oy)
        # Move toward target; also keep away from opponent to reduce contest.
        key = (-(myd2), opd2, -(abs(nx - tx) + abs(ny - ty)), -priority[(dx, dy)])
        if best_mkey is None or key > best_mkey:
            best_mkey = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]