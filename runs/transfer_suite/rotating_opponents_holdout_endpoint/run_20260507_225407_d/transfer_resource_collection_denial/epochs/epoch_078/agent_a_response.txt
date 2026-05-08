def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal or not resources:
        return [0, 0]

    def md(a, b, c, d): return abs(a - c) + abs(b - d)

    best = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        lead = do - ds  # positive means we are closer
        tie = ds
        if best is None or (lead, -tie) > (best[0], -best[1]):
            best = (lead, tie, rx, ry)
    _, _, tx, ty = best

    best_move = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)  # opponent position unchanged this turn
        # Prefer decreasing our distance; if equal, improve lead (do2 - ds2); then reduce opponent distance overall
        opp_best = min(md(ox, oy, rx, ry) for rx, ry in resources) if resources else 999
        cur_opp = md(ox, oy, tx, ty)
        if best_move is None:
            best_move = (ds2, -(do2 - ds2), cur_opp, -opp_best, dx, dy)
        else:
            cand = (ds2, -(do2 - ds2), cur_opp, -opp_best, dx, dy)
            if cand < best_move:
                best_move = cand

    return [int(best_move[4]), int(best_move[5])]