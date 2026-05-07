def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if w <= 0 or h <= 0 or not resources:
        return [0, 0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def turns(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best = None
    best_key = None

    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        best_for_move = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ot = turns(ox, oy, rx, ry)
            st = turns(nsx, nsy, rx, ry)

            # Primary: maximize advantage (opponent_time - self_time).
            adv = ot - st
            # Secondary: prefer collecting sooner; and keep advantage positive.
            key = (adv, -st, 0)

            if best_for_move is None or key > best_for_move:
                best_for_move = key

        if best_for_move is None:
            continue
        if best_key is None or best_for_move > best_key:
            best_key = best_for_move
            best = (mdx, mdy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]