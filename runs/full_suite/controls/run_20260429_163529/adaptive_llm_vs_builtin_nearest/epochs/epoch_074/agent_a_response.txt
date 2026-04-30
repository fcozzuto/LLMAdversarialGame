def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Prefer resources where we are relatively closer than opponent, with a mild "our-side" bias.
    # Our-side bias depends on starting corner: if we're closer to left, favor smaller x; else larger x.
    favor_left = 1 if sx <= w - 1 - sx else -1
    best_res = None
    best_val = None
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        side_bias = -favor_left * (rx - (w - 1) / 2.0)  # smaller for preferred side
        # Larger is better: we want (opp far) and (self near)
        val = (d_opp - d_self) + 0.12 * side_bias - 0.02 * (abs(rx - sx) + abs(ry - sy))
        if best_val is None or val > best_val:
            best_val = val
            best_res = (rx, ry)

    tx, ty = best_res

    # Move: choose delta that reduces distance-to-target while also considering opponent reachability.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        ds_next = cheb(nx, ny, tx, ty)
        ds_now = cheb(sx, sy, tx, ty)
        # Discourage stepping into a state where opponent is much closer to the same target.
        do_next = cheb(ox, oy, tx, ty)
        opp_pressure = 0.25 * (do_next - ds_next)  # higher if we become closer than opponent
        # Encourage progress (tie-break by reducing Manhattan as secondary)
        man = abs(tx - nx) + abs(ty - ny)
        prog = (ds_now - ds_next)  # positive if we get closer
        score = 1.8 * prog + opp_pressure - 0.01 * man

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]