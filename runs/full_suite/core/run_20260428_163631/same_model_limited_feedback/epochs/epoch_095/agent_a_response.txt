def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # If no resources, just drift away from opponent.
    if not resources:
        best = (0, 0, -10**9)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    oppd = cheb(nx, ny, ox, oy)
                    cand = (cheb(nx, ny, sx, sy), -oppd, oppd)
                    if cand > best:
                        best = (dx, dy, oppd)
        return [best[0], best[1]]

    # Pick a target resource we can reach sooner than opponent; else choose best tradeoff.
    best_target = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer; then closer overall; then deterministic tie-break.
        key = (-(od - sd), -sd, rx + 100 * ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                ourd = cheb(nx, ny, tx, ty)
                oppd = cheb(nx, ny, ox, oy)
                # Primary: reduce distance to target; Secondary: keep farther from opponent; Tertiary: deterministic.
                key = (-ourd, oppd, -(dx * 10 + dy))
                moves.append((key, dx, dy))
    # If somehow no moves, stay.
    if not moves:
        return [0, 0]

    moves.sort(reverse=True, key=lambda t: t[0])
    return [moves[0][1], moves[0][2]]