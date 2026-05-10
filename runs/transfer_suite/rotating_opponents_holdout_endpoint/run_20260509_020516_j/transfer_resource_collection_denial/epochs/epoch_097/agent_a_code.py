def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    def to_xy(v):
        return int(v[0]), int(v[1])

    sx, sy = to_xy(observation.get("self_position", [0, 0]))
    ox, oy = to_xy(observation.get("opponent_position", [w - 1, h - 1]))

    obstacles = set()
    for t in observation.get("obstacles") or []:
        try:
            x, y = to_xy(t)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for t in observation.get("resources") or []:
        try:
            x, y = to_xy(t)
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If we can't beat opponent on any resource now, prioritize nearest safe resource to reduce swing.
    best_target = None
    best_score = -10**18
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        margin = od - sd  # positive: we are closer
        # Favor winning margin; lightly penalize long travel.
        # Also prefer slightly toward middle to reduce being corner-trapped by obstacles.
        center_bias = - (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)) * 0.02
        score = (margin * 10) - sd + center_bias
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    tx, ty = best_target

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    allowed = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            allowed.append((dx, dy, nx, ny))

    # Choose move that best advances to target; if tie, improve margin vs opponent; then minimize distance to obstacles' vicinity.
    def obstacle_pressure(x, y):
        cnt = 0
        for ox2, oy2 in obstacles:
            if abs(ox2 - x) + abs(oy2 - y) == 1:
                cnt += 1
        return cnt

    best_move = (0, 0)
    best_move_key = None
    for dx, dy, nx, ny in allowed:
        self_to = md(nx, ny, tx, ty)
        opp_to = md(ox, oy, tx, ty)
        new_margin = opp_to - self_to
        key = (-new_margin, self_to, obstacle_pressure(nx, ny), dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]