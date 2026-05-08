def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) if abs(x1 - x2) > abs(y1 - y2) else max(abs(x1 - x2), abs(y1 - y2))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick a target that is close to us, and (secondarily) farther from the opponent.
    best_t = None
    best_key = None
    for rx, ry in resources:
        my_d = max(abs(rx - sx), abs(ry - sy))
        op_d = max(abs(rx - ox), abs(ry - oy))
        key = (my_d, -op_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    rx, ry = best_t

    my_now = max(abs(rx - sx), abs(ry - sy))
    op_now = max(abs(rx - ox), abs(ry - oy))
    opp_ahead = op_now < my_now

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = max(abs(rx - nx), abs(ry - ny))
        d_opp = max(abs(rx - ox), abs(ry - oy))
        # Evaluate our move only: if opponent is closer, prioritize reducing opponent advantage by minimizing our distance.
        w1, w2 = (4, 1) if not opp_ahead else (7, 2)
        # Also nudge away from letting the opponent be too close to the target (proxy).
        val = w1 * d_self + w2 * d_opp
        # Tie-break: prefer reducing (d_opp - d_self) and then moving closer.
        tie = (d_self, -(d_opp - d_self), nx, ny)
        cand = (val, tie)
        if best_val is None or cand < best_val:
            best_val = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]