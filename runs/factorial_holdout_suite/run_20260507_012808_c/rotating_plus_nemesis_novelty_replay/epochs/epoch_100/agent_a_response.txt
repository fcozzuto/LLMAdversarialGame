def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [int(dx), int(dy)]

    # Pick a target resource that maximizes likelihood of reaching before opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        # tie-break favor closer overall, and slight preference for smaller coordinates deterministically
        key = (opd - myd) * 1000 - myd * 3 - rx * 0.01 - ry * 0.0001
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Choose one-step move by evaluating next position against target and nearby alternatives.
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd_next = manh(nx, ny, tx, ty)
        opd = manh(ox, oy, tx, ty)
        # also consider "pressure" on nearest resource from next spot
        nearest_my = 10**9
        nearest_op = 10**9
        for rx, ry in resources:
            d1 = manh(nx, ny, rx, ry)
            if d1 < nearest_my: nearest_my = d1
            d2 = manh(ox, oy, rx, ry)
            if d2 < nearest_op: nearest_op = d2
        score = (opd - myd_next) * 1000 - nearest_my * 2 + (nearest_op - nearest_my) * 5
        # deterministic tie-break: prefer moves with smallest dx then dy toward target (but stable)
        tieb = (abs(nx - tx) + abs(ny - ty), abs(dx), abs(dy), dx, dy)
        full = (score, -tieb[0], -tieb[1], -tieb[2], -tieb[3], -tieb[4])
        if best_score is None or full > best_score:
            best_score = full
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]