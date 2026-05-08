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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        return [0, 0]

    # Pick a target resource to race: maximize how much earlier we can arrive than opponent.
    best_target = None
    best_key = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d  # positive: we closer
        # Slightly prefer resources that are not "instant" for opponent and are closer for us.
        key = (-adv, my_d, dist8(ox, oy, rx, ry), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # Choose move that maximizes immediate post-move advantage to the target,
    # with small tie-break to keep distance from opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_d_next = dist8(nx, ny, tx, ty)
        op_d_next = dist8(ox, oy, tx, ty)
        target_adv_next = op_d_next - my_d_next

        # Prefer safer positions vs opponent when target race is tied.
        my_to_opp = dist8(nx, ny, ox, oy)

        # Also avoid stepping directly adjacent to an obstacle corner case: simple penalty if landing on obstacle already prevented.
        val = (target_adv_next, my_to_opp, -my_d_next, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]