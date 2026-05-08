def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        return [0, 0]

    # Prefer resources we can reach sooner; otherwise, deny by moving toward contested resources.
    best = None
    best_score = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        # Score: advantage first, then my closeness, then deterministic tie on coords
        score = ((op_d - my_d), -my_d, -abs(rx - ox) - abs(ry - oy), rx, ry)
        if best_score is None or score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best

    # Move greedily but with a contention-aware tie-break: maximize immediate advantage.
    best_m = (0, 0)
    best_mscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = dist8(nx, ny, tx, ty)
        my_adv_next = dist8(ox, oy, tx, ty) - nd
        # If target is contested, step that maximizes advantage; otherwise step that reduces distance.
        dist_key = -nd
        tie = (abs(nx - ox) + abs(ny - oy))  # also avoid getting too close to opponent if equally good
        mscore = (my_adv_next, dist_key, -tie)
        if best_mscore is None or mscore > best_mscore:
            best_mscore = mscore
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]