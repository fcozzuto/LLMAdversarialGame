def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        # mode: secure if we can arrive earlier; otherwise denial by maximizing op lag.
        if my_d < op_d:
            key = (0, my_d, op_d, rx, ry)
        else:
            # Deny: choose target where opponent is not too close relative to us (largest gap), then closer to us.
            key = (1, -(op_d - my_d), my_d, op_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Greedy step: in secure mode, minimize our distance; in denial mode, also increase opponent distance.
    my_d = dist(sx, sy, tx, ty)
    op_d = dist(ox, oy, tx, ty)
    secure_mode = my_d < op_d

    best_move = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd_my = dist(nx, ny, tx, ty)
        # Secondary terms for obstacle-robustness and tie-breaking stability
        if secure_mode:
            score = (nd_my, -dist(nx, ny, ox, oy), abs(dx) + abs(dy), rx := tx, ry := ty)
        else:
            nd_op = dist(nx, ny, ox, oy)
            # Actually "deny" by pushing ourselves to make opponent farther from the target (via our move reducing contestedness).
            # Since we can't control opponent directly, we maximize opponent distance to target minus our distance to target.
            opp_to_target = dist(ox, oy, tx, ty)
            score = (nd_my - (opp_to_target - nd_my), -opp_to_target, abs(dx) + abs(dy), tx, ty)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]