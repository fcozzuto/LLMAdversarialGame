def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d  # we prefer to be sooner (adv small/negative is bad; positive is good)
        # Key: maximize (we arrive earlier) => minimize adv' where larger adv is better -> use -adv
        # Also bias toward nearer targets for determinism.
        key = (-adv, my_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # If opponent is significantly closer, try to "block" by heading to the cell that we can reach
    # while still making progress toward the target; we don't know paths, so use one-step lookahead.
    best_move = (10**9, None, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to = dist8(nx, ny, tx, ty)
        my_d_now = dist8(sx, sy, tx, ty)
        op_d_now = dist8(ox, oy, tx, ty)
        adv_now = op_d_now - my_d_now
        adv_next = dist8(ox, oy, tx, ty) - d_to
        # Prefer moves that reduce distance to target; if tied, prefer increasing our advantage.
        key = (d_to, -adv_next, abs(nx - tx) + abs(ny - ty), nx, ny)
        if key < (best_move[0], best_move[2], best_move[3], best_move[1] or -1, -1):
            best_move = (key[0], (dx, dy), key[2], key[3])
    if best_move[1] is None:
        return [0, 0]
    return [int(best_move[1][0]), int(best_move[1][1])]