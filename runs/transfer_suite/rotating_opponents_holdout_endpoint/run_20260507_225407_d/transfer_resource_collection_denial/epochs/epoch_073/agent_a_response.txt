def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # If no resources visible, drift toward center/escape corners deterministically.
    if not res:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = max(abs(nx - tx), abs(ny - ty))
            key = (d, dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    def cheb(a, b, c, d):
        a, b, c, d = int(a), int(b), int(c), int(d)
        return max(abs(a - c), abs(b - d))

    best_move = None
    best_key = None
    # Score a move by the best "first-claim advantage" it creates over visible resources.
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_for_move = None
        for tx, ty in res:
            self_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            adv = opp_d - self_d  # higher means more likely to arrive first
            # Prefer resources where we are closer too; deterministic tie-break by coords.
            key = (adv, -self_d, -((tx << 3) + ty))
            if best_for_move is None or key > best_for_move:
                best_for_move = key
        # Prefer moves with higher advantage; then closer; then deterministic dx/dy.
        overall = (best_for_move[0], best_for_move[1], dx, dy)
        if best_key is None or overall > best_key:
            best_key = overall
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]