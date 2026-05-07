def choose_move(observation):
    w = int(observation.get("grid_width") or 0)
    h = int(observation.get("grid_height") or 0)
    if w <= 0: w = 8
    if h <= 0: h = 8

    p = observation.get("self_position") or [0, 0]
    q = observation.get("opponent_position") or [0, 0]
    sx, sy = int(p[0]), int(p[1])
    ox, oy = int(q[0]), int(q[1])

    blocked = set()
    for o in observation.get("obstacles") or []:
        try:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))
        except:
            pass

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    if not moves:
        return [0, 0]
    if not resources:
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    my = (sx, sy)
    him = (ox, oy)
    resources.sort(key=lambda t: (cheb(my, t), cheb(him, t), t[0], t[1]))
    resources = resources[:20]

    best = None
    best_move = (0, 0)
    for dx, dy in moves + [(0, 0)]:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nm = (nx, ny)

        # Pick best target for this move; key prefers higher advantage for opponent vs us (d_op - d_me)
        best_for_move = None
        for t in resources:
            d_me = cheb(nm, t)
            d_op = cheb(him, t)
            adv = d_op - d_me
            # Prefer grabbing if we are not worse; also prefer closer to target when equally safe
            k = (adv, -d_me, -abs(t[0] - ox) - abs(t[1] - oy), -(t[0] * 1000 + t[1]))
            if best_for_move is None or k > best_for_move:
                best_for_move = k

        if best_for_move is None:
            continue
        if best is None or best_for_move > best:
            best = best_for_move
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]