def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    if resources:
        cx, cy = w // 2, h // 2
        best = (None, -10**9)
        for rx, ry in resources:
            sd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            lead = od - sd
            center_bias = -abs(rx - cx) - abs(ry - cy)
            score = lead * 1000 + center_bias * 10
            if score > best[1]:
                best = ((rx, ry), score)
        tx, ty = best[0]
    else:
        tx, ty = w // 2, h // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestd = 10**9
    bestlead = -10**9
    bestmove = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_me = dist(nx, ny, tx, ty)
        d_op = dist(ox, oy, tx, ty)
        lead = d_op - d_me
        if d_me < bestd or (d_me == bestd and lead > bestlead) or (d_me == bestd and lead == bestlead and (dx, dy) < bestmove):
            bestd = d_me
            bestlead = lead
            bestmove = (dx, dy)
    dx, dy = bestmove
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    if not ok(sx + dx, sy + dy):
        dx, dy = 0, 0
    return [int(dx), int(dy)]