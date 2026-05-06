def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obs_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obs_list)

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_r = None
    best_key = None

    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        secure = 0 if sd <= od else 1  # secure first
        adv = od - sd
        # Counter "row sweeping": if same row as opponent, slightly deprioritize (they can skim/capture).
        row_pen = 1 if ry == oy and (sd <= od + 1) else 0
        # Mild center-ish bias to keep options open (deterministic tie-break).
        center_bias = abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)
        key = (secure, sd, -adv, row_pen, center_bias, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        best_r = resources[0]
    rx, ry = best_r

    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        secure = 0 if myd <= opd else 1
        # Prefer reducing my distance; also avoid stepping into opponent's row/col lanes.
        lane_pen = 0
        if ny == oy and rx != nx:
            lane_pen += 1
        if nx == ox and ry != ny:
            lane_pen += 1
        mkey = (secure, myd, lane_pen, - (opd - myd), rx, ry, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]