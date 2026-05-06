def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    legal = []
    for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            # Prefer resources closer to us and farther from opponent (race bias)
            v = myd - 0.65 * opd
            if best is None or v < best[0] or (v == best[0] and (myd < best[2])):
                best = (v, (rx, ry), myd)
        tx, ty = best[1]
    else:
        # No resources: move toward opponent corner direction deterministically
        tx, ty = ox, oy

    # Choose move that most reduces distance to target; if tie, maximize opponent distance.
    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        myd = md(nx, ny, tx, ty)
        opd = md(nx, ny, ox, oy)
        # Secondary: prefer not to drift too much from target alignment
        align = - (abs(nx - tx) + abs(ny - ty))
        key = (myd, -opd, -align)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]