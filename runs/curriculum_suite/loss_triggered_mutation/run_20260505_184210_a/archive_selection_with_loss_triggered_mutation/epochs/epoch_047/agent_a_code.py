def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if (observation.get("turn_index", 0) or 0) % 2:
        moves = [moves[4]] + moves[:4] + moves[5:]  # deterministic slight reshuffle

    def best_for_target(nx, ny, tx, ty):
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # Prefer getting strictly closer than opponent, else still approach.
        gain = (d_op - d_me)
        # Tie-break toward targets nearer to the opponent (less likely contested later).
        return 3.0 * gain - 0.15 * d_me - 0.03 * cheb(ox, oy, tx, ty)

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate best target from this move.
        mv = -10**18
        # Small deterministic pruning: only consider a few closest resources to our position.
        dlist = []
        for tx, ty in resources:
            dlist.append((cheb(nx, ny, tx, ty), tx, ty))
        dlist.sort(key=lambda t: t[0])
        for i in range(0, min(6, len(dlist))):
            _, tx, ty = dlist[i]
            v = best_for_target(nx, ny, tx, ty)
            if v > mv:
                mv = v
        # If all else equal, avoid stepping away from center to reduce path oscillation.
        center_bias = -0.01 * cheb(nx, ny, (w - 1) / 2.0, (h - 1) / 2.0)  # float but deterministic
        total = mv + center_bias
        if total > best_val:
            best_val = total
            best_move = [dx, dy]

    return best_move