def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = w - 1 if ox < sx else 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        ty = (h - 1) if oy < sy else 0
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if dx == 0 and dy == 0:
            return [0, 0]
        return [dx, dy]

    # Bias away from opponent sweep by targeting cells where we are relatively closer.
    best = None
    best_key = None
    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        line_bias = 0
        if x == sx or y == sy:
            line_bias = -0.25  # slightly prefer continuing along useful lines
        if x == ox or y == oy:
            line_bias = line_bias + 0.15  # avoid giving them easy overlap
        # Maximize margin (od - sd), then prefer smaller sd to secure pickup first.
        margin = od - sd
        key = (-(margin + line_bias), sd, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If diagonal step is blocked, take best axis-aligned alternative deterministically.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        cand = []
        axx = 0 if tx == sx else (1 if tx > sx else -1)
        axy = 0
        cand.append((abs(tx - (sx + axx)) + abs(ty - (sy + axy)), axx, axy))
        byx = 0
        byy = 0 if ty == sy else (1 if ty > sy else -1)
        cand.append((abs(tx - (sx + byx)) + abs(ty - (sy + byy)), byx, byy))
        if dx == 0 or dy == 0:
            # try staying in place first
            if (sx + dx, sy + dy) in obstacles:
                return [0, 0]
        cand.sort()
        _, dx, dy = cand[0]
    return [int(dx), int(dy)]