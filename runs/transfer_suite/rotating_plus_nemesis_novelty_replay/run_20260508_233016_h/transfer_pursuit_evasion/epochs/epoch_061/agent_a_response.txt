def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    if sx == ox and sy == oy:
        return [0, 0]

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def neighbors(px, py):
        out = []
        for dx, dy in deltas:
            nx, ny = px + dx, py + dy
            if legal(nx, ny):
                out.append((nx, ny))
        return out

    my_neighbors = neighbors(sx, sy)
    if not my_neighbors:
        return [0, 0]

    best = None
    best_tuple = None  # (worst_dist2_after_evader, -min_dist2_after_evader, tie_center)

    for nx, ny in my_neighbors:
        # depth-1 minimax: evader picks move maximizing our distance
        worst = -1
        best_min = None
        for mx, my in neighbors(ox, oy):
            d = dist2(nx, ny, mx, my)
            if d > worst:
                worst = d
            # Track also evader's choice that minimizes our eventual worst-case already captured by worst,
            # but we use this for tie-breaking by favoring moves that keep distance low in best evader replies.
            if best_min is None or d < best_min:
                best_min = d

        # tie-break: prefer smaller worst; then smaller best_min; then move toward opponent (greedy)
        center_tie = dist2(nx, ny, ox, oy)
        tup = (worst, best_min if best_min is not None else worst, center_tie)
        if best_tuple is None or tup < best_tuple:
            best_tuple = tup
            best = (nx, ny)

    dx, dy = best[0] - sx, best[1] - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    if not legal(sx + dx, sy + dy):
        # fallback deterministic: greedy step toward opponent among legal
        step = [0, 0]
        bestg = None
        for ddx, ddy in deltas:
            nx, ny = sx + ddx, sy + ddy
            if not legal(nx, ny):
                continue
            g = dist2(nx, ny, ox, oy)
            if bestg is None or g < bestg or (g == bestg and (ddx, ddy) < (step[0], step[1])):
                bestg = g
                step = [ddx, ddy]
        return step
    return [int(dx), int(dy)]