def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    # Choose target resource with "good for us, bad for them"
    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        oppd = man(ox, oy, rx, ry)
        # smaller key is better
        key = (myd + 2 * oppd, myd, -oppd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Prefer approaching chosen target, while increasing opponent distance to it.
        my_to_t = man(nx, ny, tx, ty)
        opp_to_t = man(ox, oy, tx, ty)

        # Also consider immediate closeness to any resource (helps when target shifts).
        min_my_to_any = None
        min_opp_to_any = None
        for rx, ry in resources:
            dmy = man(nx, ny, rx, ry)
            dob = man(ox, oy, rx, ry)
            if min_my_to_any is None or dmy < min_my_to_any:
                min_my_to_any = dmy
            if min_opp_to_any is None or dob < min_opp_to_any:
                min_opp_to_any = dob

        val = (my_to_t * 3 + min_my_to_any, -opp_to_t, -min_opp_to_any, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    # If all candidate moves were blocked, stay put (engine keeps in place).
    return best_move