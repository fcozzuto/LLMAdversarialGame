def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(w - 1, h - 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    centerx, centery = (w - 1) / 2.0, (h - 1) / 2.0

    # Opponent's likely target: closest remaining resource to opponent.
    best_t = None
    best_do = 10**9
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if d < best_do:
            best_do = d
            best_t = (rx, ry)
    tx, ty = best_t if best_t else (w - 1, h - 1)

    myd = cheb(sx, sy, tx, ty)
    behind = (myd > best_do)  # only act defensively if opponent is closer

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if behind:
            # Defensive: maximize separation from opponent and reduce their immediate access to tx,ty.
            val = (cheb(nx, ny, ox, oy) * 10) - (cheb(nx, ny, tx, ty) * 2)
        else:
            # Offensive: maximize lead over opponent on the best resource we can reach earliest.
            val = -10**9
            for rx, ry in resources:
                dme = cheb(nx, ny, rx, ry)
                dop = cheb(ox, oy, rx, ry)
                lead = dop - dme
                # Prefer larger lead; small distances to center as deterministic tiebreak.
                t = lead * 100 - dme - int(abs(nx - centerx) + abs(ny - centery))
                if t > val:
                    val = t
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]