def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = set((p[0], p[1]) for p in obstacles)

    def man_dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick target where we are currently most ahead in Manhattan distance.
    best = None
    for rx, ry in resources:
        my_d = man_dist(sx, sy, rx, ry)
        op_d = man_dist(ox, oy, rx, ry)
        # Prefer large advantage; then closer overall; then deterministic coord tie-break.
        key = (op_d - my_d, -my_d, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # One-step lookahead: move that maximizes our advantage at the target.
    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    cur_my = man_dist(sx, sy, tx, ty)

    best_move = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        my_next = man_dist(nx, ny, tx, ty)

        # Approximate opponent best response: assume opponent also moves one step greedily toward target.
        # This is deterministic and cheap; doesn't need their legal moves explicitly.
        op_curr = man_dist(ox, oy, tx, ty)
        if op_curr == 0:
            op_next = 0
        else:
            best_op = None
            for odx, ody in deltas:
                px, py = ox + odx, oy + ody
                if px < 0 or px >= w or py < 0 or py >= h:
                    continue
                if (px, py) in obs_set:
                    continue
                d = man_dist(px, py, tx, ty)
                if best_op is None or d < best_op:
                    best_op = d
            op_next = best_op if best_op is not None else op_curr

        advantage = op_next - my_next  # higher is better
        progress = cur_my - my_next    # prefer moving closer if advantage ties
        # Deterministic tie-break favors moves that are closer to center of board.
        center_bias = -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
        key = (advantage, progress, center_bias, -my_next, dx, dy)

        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]