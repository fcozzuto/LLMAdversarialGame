def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation["resources"]
    obs_list = observation["obstacles"]
    obstacles = set((x, y) for x, y in obs_list)
    ox, oy = observation["opponent_position"]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    best_target = None
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        key = (myd - opd, myd, rx, ry)
        if best_target is None or key < best_target[0]:
            best_target = (key, (rx, ry))
    tx, ty = best_target[1]

    curd = dist(sx, sy, tx, ty)
    best_move = [0, 0]
    best_key = (10**9, 10**9, 10**9, 10**9)

    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                continue
            if not valid(nx, ny):
                continue
            myd_new = dist(nx, ny, tx, ty)
            opd_new = dist(ox, oy, tx, ty)
            # Prefer moves that reduce my advantage gap; tie-break toward nearer target.
            gap_new = myd_new - opd_new
            # Also lightly avoid stepping away from the target.
            step_key = (gap_new, myd_new, abs(nx - tx) + abs(ny - ty), nx, ny)
            if step_key < best_key and (myd_new <= curd or step_key[0] < best_key[0]):
                best_key = step_key
                best_move = [dx, dy]

    # If no improving move found (all paths blocked), stay.
    if best_key[0] == 10**9:
        return [0, 0]
    return best_move