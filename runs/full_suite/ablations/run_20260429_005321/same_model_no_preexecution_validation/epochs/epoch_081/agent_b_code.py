def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def cell_ok(x, y): return inb(x, y) and (x, y) not in obstacles
    def block_pen(x, y):
        c = 0
        for dx, dy in dirs:
            xx, yy = x + dx, y + dy
            if (xx, yy) in obstacles: c += 1
        return c

    def pick_target(px, py):
        if not resources:
            return (w // 2, h // 2)
        best = resources[0]; bestv = -10**18
        for rx, ry in resources:
            d_me = cheb(px, py, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources where we are relatively closer; also avoid being too far.
            v = (d_op - d_me) * 12 - d_me * 1.2 - 0.7 * block_pen(rx, ry)
            if v > bestv or (v == bestv and (rx, ry) < best):
                bestv = v; best = (rx, ry)
        return best

    tx, ty = pick_target(sx, sy)

    best_move = (0, 0); best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        # Main: get closer to chosen target; Secondary: improve contested advantage.
        d_t = cheb(nx, ny, tx, ty)
        d_t0 = cheb(sx, sy, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # If we reduce our distance without letting opponent gain the contest, we score higher.
        v = (d_op - d_t) * 10 - d_t * 0.9 + (d_t0 - d_t) * 2.2 - 0.8 * block_pen(nx, ny)
        # Tie-break deterministically by preferring forward progress toward target, then lexicographic move.
        if v > best_score:
            best_score = v; best_move = (dx, dy)
        elif v == best_score:
            # lexicographic on (dx,dy) for determinism
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]