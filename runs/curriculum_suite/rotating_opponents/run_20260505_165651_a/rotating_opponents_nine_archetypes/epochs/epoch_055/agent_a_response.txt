def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def dist8(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not moves:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            key = (dist8(nx, ny, cx, cy), dist8(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Prefer resources where we are closer than opponent; otherwise reduce the gap.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        my_d = 10**9
        opp_d = 10**9
        rel = 10**9
        target = None

        for rx, ry in resources:
            d1 = dist8(nx, ny, rx, ry)
            d2 = dist8(ox, oy, rx, ry)
            # win-urgency: aim for resources with (my_d - opp_d) as small as possible
            gap = d1 - d2
            # if we're not behind, strongly prioritize; else minimize how far behind we are
            urgency = gap if gap <= 0 else 3 * gap + d1
            key_here = (urgency, d1, d2, rx, ry)
            if target is None or key_here < target[0]:
                target = (key_here, d1, d2)

        my_d, opp_d = target[1], target[2]
        # Encourage moving that reduces distance to chosen target and blocks by avoiding being adjacent to obstacles poorly.
        score_key = (my_d - opp_d, my_d, -opp_d, dx, dy, nx, ny)
        if best is None or score_key < best[0]:
            best = (score_key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]