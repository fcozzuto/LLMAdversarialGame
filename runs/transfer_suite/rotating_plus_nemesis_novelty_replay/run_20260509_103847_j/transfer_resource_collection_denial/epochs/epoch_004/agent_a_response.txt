def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    best_res = None
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        # Prefer resources where we are closer (maximize opd-myd). Tie by smaller myd.
        key = (-(opd - myd), myd, rx, ry)
        if best_res is None or key < best_res[0]:
            best_res = (key, (rx, ry))
    tx, ty = best_res[1]

    best_move = (0, 0)
    best_key = None
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            myd_new = dist(nx, ny, tx, ty)
            opd_new = dist(ox, oy, tx, ty)
            # Primary: keep/extend advantage (minimize myd_new - opd_new).
            adv_key = (myd_new - opd_new, myd_new, abs(dx) + abs(dy), dx, dy, nx, ny)
            if best_key is None or adv_key < best_key:
                best_key = adv_key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]