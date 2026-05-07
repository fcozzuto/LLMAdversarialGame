def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
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

    best = None
    best_key = (-10**9, -10**9, -10**9, -10**9)
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        spread = abs(ry - oy) + abs(rx - ox)
        # Bias to split: prefer resources that are "off" the opponent's likely lane.
        lane_bias = 0
        if (ry % 2) == (oy % 2):
            lane_bias = -1
        # Deterministic max key
        key = (adv, spread + lane_bias, -sd, -rx - ry)
        if key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    dy = 0
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    deltas = [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, dy), (dx, -dy), (-dx, 0), (0, -dy), (-dx, -dy)]
    deltas2 = []
    for d in deltas:
        if d not in deltas2:
            deltas2.append(d)

    best_move = (0, 0)
    best_md = 10**9
    for mx, my in deltas2:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            md = cheb(nx, ny, tx, ty)
            # Prefer moves that don't step backward in Chebyshev distance
            back_pen = 0
            if md > cheb(sx, sy, tx, ty):
                back_pen = 1
            md2 = md + back_pen
            if md2 < best_md:
                best_md = md2
                best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]