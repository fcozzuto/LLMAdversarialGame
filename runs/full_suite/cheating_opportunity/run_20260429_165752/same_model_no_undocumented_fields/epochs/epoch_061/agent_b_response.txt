def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    def dist_m(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    cx, cy = (w - 1) // 2, (h - 1) // 2
    parity = int(observation.get("turn_index") or 0) & 1

    if resources:
        best = None
        best_val = -10**9
        for rx, ry in resources:
            sd = dist_m(sx, sy, rx, ry)
            od = dist_m(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; if parity flips, slightly favor grabbing race-front.
            val = (od - sd) * (2 if parity == 0 else 1) - sd * (1 if parity == 1 else 0)
            if val > best_val:
                best_val = val
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = cx, cy

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_self = dist_m(nx, ny, tx, ty)
        d_opp = dist_m(ox, oy, tx, ty)
        adv = (d_opp - d_self)
        # Also lightly prefer moves that reduce our distance to center to avoid dead-ends.
        center_bias = -((abs(nx - cx) + abs(ny - cy)) * (1 if parity == 0 else 0))
        # Deterministic tie-breaker: prefer lexicographically smaller move list index via score offsets.
        score = adv * 1000 - d_self + center_bias + (-0.000001) * (dx + 2 * dy)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move