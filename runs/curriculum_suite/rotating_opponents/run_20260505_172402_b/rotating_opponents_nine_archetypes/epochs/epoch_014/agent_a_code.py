def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def dist(a, b, c, d):
        dx = c - a
        if dx < 0:
            dx = -dx
        dy = d - b
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    my_d0 = dist(sx, sy, ox, oy)
    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        key = (opd - myd, -myd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = [0, 0]
    best_mkey = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        myd1 = dist(nx, ny, tx, ty)
        opd1 = dist(ox, oy, tx, ty)

        # Prefer reducing our distance; also prefer not letting opponent have an advantage.
        # Small tie-breaker: keep some distance from opponent unless it doesn't matter.
        margin = opd1 - myd1
        key = (margin, -myd1, my_d0, -abs(nx - tx) - abs(ny - ty), -nx, -ny)
        if best_mkey is None or key > best_mkey:
            best_mkey = key
            best_m = [dx, dy]

    return best_m