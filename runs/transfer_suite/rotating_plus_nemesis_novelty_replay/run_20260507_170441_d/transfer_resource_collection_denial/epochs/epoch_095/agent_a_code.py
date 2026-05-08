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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def best_step_for_target(tx, ty):
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            my = dist8(nx, ny, tx, ty)
            opp = dist8(nx, ny, ox, oy)
            v = (-my, -opp, dx, dy)
            if v > (bestv, bestv, -10**18, -10**18):
                bestv = v[0]
                best = (dx, dy)
        return [best[0], best[1]]

    if not resources:
        # Deny: move toward the closest of the two far corners (toward opponent side)
        tx = w - 1 if sx <= (w - 1) // 2 else 0
        ty = h - 1 if sy <= (h - 1) // 2 else 0
        tx2 = 0 if tx == w - 1 else w - 1
        ty2 = 0 if ty == h - 1 else h - 1
        target = (tx, ty) if dist8(sx, sy, tx, ty) <= dist8(sx, sy, tx2, ty2) else (tx2, ty2)
        return best_step_for_target(target[0], target[1])

    # Choose resource where we are most ahead; if behind, pick resource we can still contest soon.
    best_r = None
    best_key = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        opp_d = dist8(ox, oy, rx, ry)
        # primary: advantage (opp farther is good). secondary: closeness to arrive quickly.
        key = (opp_d - my_d, -my_d, -(abs(rx - (w - 1 - sx)) + abs(ry - (h - 1 - sy))))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    # Move greedily toward chosen resource; if the move would step into immediate disadvantage, fall back one.
    dxdy = best_step_for_target(best_r[0], best_r[1])
    nx, ny = sx + dxdy[0], sy + dxdy[1]
    my_after = dist8(nx, ny, best_r[0], best_r[1])
    opp_after = dist8(ox, oy, best_r[0], best_r[1])
    if my_after > opp_after:
        # Fallback: choose a move that maximizes advantage on the same resource.
        best = [0, 0]
        best_adv = -10**18
        for dx, dy in moves:
            tx, ty = sx + dx, sy + dy
            if not ok(tx, ty):
                continue
            adv = dist8(ox, oy, best_r[0], best_r[1]) - dist8(tx, ty, best_r[0], best_r[1])
            if adv > best_adv or (adv == best_adv and (dx, dy) < (best[0], best[1])):
                best_adv = adv
                best = [dx, dy]
        return best
    return dxdy