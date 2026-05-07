def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Depth-1 lookahead: choose step that maximizes our eventual race advantage (greedy on next position).
    best = None
    best_move = [0, 0]
    t = int(observation.get("turn_index", 0) or 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny = sx, sy
        # Advantage measure: larger is better.
        # We take best target after this move; add slight penalty to keep progress deterministic and decisive.
        cur_best = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            val = (od - sd)
            # tie-break: prefer smaller sd, and prefer higher val
            adj = val * 10 - sd - 0.01 * (t + rx * 3 + ry * 5)
            if cur_best is None or adj > cur_best:
                cur_best = adj
        if cur_best is None:
            continue
        # Tiny deterministic bias to prefer staying on-board diagonally towards center when close.
        center_bias = -0.001 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
        score = cur_best + center_bias
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move