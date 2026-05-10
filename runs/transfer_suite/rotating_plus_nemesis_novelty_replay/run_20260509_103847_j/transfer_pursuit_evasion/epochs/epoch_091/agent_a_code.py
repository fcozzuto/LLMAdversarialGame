def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role) or ("runner" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y):
        ax = abs(x - ox)
        ay = abs(y - oy)
        return ax if ax > ay else ay

    if is_evader:
        target = max(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), c[0], c[1]))
        tx, ty = target
        best = None  # (primary, tie, dx, dy)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            dist = cheb(nx, ny)
            corner_bias = abs(nx - tx) + abs(ny - ty)
            primary = (dist, -corner_bias)
            tie = (nx, ny)
            if best is None or primary > best[0] or (primary == best[0] and tie < best[1]):
                best = (primary, tie, dx, dy)
        if best is None:
            return [0, 0]
        return [best[2], best[3]]
    else:
        best = None  # (primary, tie, dx, dy)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            dist = cheb(nx, ny)
            primary = (-dist, -abs(nx - ox) - abs(ny - oy))  # maximize negative cheb then negative manhattan
            tie = (nx, ny)
            if best is None or primary > best[0] or (primary == best[0] and tie < best[1]):
                best = (primary, tie, dx, dy)
        if best is None:
            return [0, 0]
        return [best[2], best[3]]