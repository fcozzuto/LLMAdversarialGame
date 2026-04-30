def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obst = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    legal = []
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    # Target selection: pick a resource where we have a "reach advantage" over opponent.
    if resources:
        best_tx, best_ty = resources[0]
        best_val = None
        for rx, ry in resources:
            myd = d2(x, y, rx, ry)
            opd = d2(ox, oy, rx, ry)
            # Favor larger opponent distance and smaller our distance; slight penalty for being far.
            val = (opd - myd) * 2 - myd // 3
            if best_val is None or val > best_val or (val == best_val and (rx, ry) < (best_tx, best_ty)):
                best_val = val
                best_tx, best_ty = rx, ry
        tx, ty = best_tx, best_ty
    else:
        # No resources: move toward center to avoid dead zones.
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0

    # If extremely close to opponent, prioritize moving away.
    close = d2(x, y, ox, oy) <= 4

    best_move = (0, 0)
    best_score = None
    for dx, dy in legal:
        nx, ny = x + dx, y + dy
        if close:
            # Maximize distance from opponent; tie-break toward reducing distance to target.
            score = (d2(nx, ny, ox, oy), -d2(nx, ny, tx, ty))
        else:
            # Minimize distance to target; tie-break by maximizing distance from opponent.
            score = (-d2(nx, ny, tx, ty), d2(nx, ny, ox, oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]