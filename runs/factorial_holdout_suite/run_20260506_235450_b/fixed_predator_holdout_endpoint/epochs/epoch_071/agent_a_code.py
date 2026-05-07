def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        my_d = []
        for tx, ty in res:
            my_next = manh(nx, ny, tx, ty)
            opp_next = manh(ox, oy, tx, ty)
            advantage = opp_next - my_next  # bigger is better
            # If we can grab it immediately, heavily prioritize.
            grab = 5 if my_next == 0 else (2 if my_next <= 1 else 0)
            # Slightly discourage moving away from the currently best resource.
            tie = -0.01 * (my_next)
            my_d.append((advantage + grab + tie, my_next, tx, ty))
        my_d.sort(reverse=True, key=lambda t: (t[0], -t[1]))
        val = my_d[0][0] if my_d else -10**18

        if val > best_val:
            best_val = val
            best_move = (dx if (nx, ny) != (sx, sy) else 0, dy if (nx, ny) != (sx, sy) else 0)

    # Deterministic secondary: move with minimal my distance to the best target
    tx_best = None
    ty_best = None
    for tx, ty in res:
        if tx_best is None:
            tx_best, ty_best = tx, ty
        else:
            a = (manh(sx, sy, ox, oy), -manh(sx, sy, tx, ty))
            b = (manh(sx, sy, ox, oy), -manh(sx, sy, tx_best, ty_best))
            if b[1] < a[1]:
                tx_best, ty_best = tx, ty
    dx, dy = best_move
    # If best_move was stay, still head one step toward the best advantage resource deterministically
    if dx == 0 and dy == 0:
        best_t = None
        best_adv = -10**18
        for tx, ty in res:
            adv = (manh(ox, oy, tx, ty) - manh(sx, sy, tx, ty))
            if adv > best_adv:
                best_adv = adv
                best_t = (tx, ty)
        tx, ty = best_t
        mdx = 0 if tx == sx else (1 if tx > sx else -1)
        mdy = 0 if ty == sy else (1 if ty > sy else -1)
        if (sx + mdx, sy + mdy) in obstacles and (sx + mdx, sy) not in obstacles:
            mdy = 0
        if (sx + mdx, sy + mdy) in obstacles and (sx, sy + mdy) not in obstacles:
            mdx = 0
        if (sx + mdx, sy + mdy) in obstacles:
            mdx = 0
            mdy = 0
        return [int(mdx), int(mdy)]

    return [int(best_move[0]), int(best_move[1])]