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
    if not resources:
        return [0, 0]

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # If opponent is closer to their best remaining resource, prioritize denying it by moving toward it.
    # Otherwise, race for the resource that maximizes (op_d - my_d).
    def best_resource_for(posx, posy):
        best = None
        for rx, ry in resources:
            d = dist8(posx, posy, rx, ry)
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        return best[1]

    deny_tx, deny_ty = best_resource_for(ox, oy)

    # Evaluate each move using a two-part deterministic score.
    # Primary: maximize best (op_d - my_d) across all resources after the move.
    # Secondary: minimize my distance to the best "deny" target.
    # Tertiary: minimize my distance overall (tie-break).
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_best_adv = -10**9
        my_best_d = 10**9
        for rx, ry in resources:
            my_d = dist8(nx, ny, rx, ry)
            op_d = dist8(ox, oy, rx, ry)
            adv = op_d - my_d
            if adv > my_best_adv or (adv == my_best_adv and my_d < my_best_d):
                my_best_adv = adv
                my_best_d = my_d
        deny_d = dist8(nx, ny, deny_tx, deny_ty)
        key = (-my_best_adv, deny_d, my_best_d, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]