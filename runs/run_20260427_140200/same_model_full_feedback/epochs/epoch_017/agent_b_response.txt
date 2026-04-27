def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    if not resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # Prefer moving away from opponent
            v = cheb(nx, ny, ox, oy)
            if best is None or v > best[0] or (v == best[0] and (dx, dy) < best[1]):
                best = (v, (dx, dy))
        return [best[1][0], best[1][1]]

    # Choose move by evaluating one-step transition toward favorable resources.
    # Favor resources where we are currently closer than opponent; otherwise minimize relative disadvantage.
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        move_val = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we are closer, prioritize; if not, still minimize the gap.
            rel = do - ds  # higher is better
            # Penalize letting opponent reach very soon; prefer keeping distance.
            ppen = 0
            if do <= 1:
                ppen = 3
            # Overall value: maximize rel, then minimize ds, then prefer farther from opponent.
            val = rel * 10 - ppen - ds
            # Tie-break: deterministic on position
            if move_val is None or val > move_val[0] or (val == move_val[0] and (ds, -cheb(nx, ny, ox, oy), rx, ry) < move_val[1]):
                move_val = (val, (ds, -cheb(nx, ny, ox, oy), rx, ry))
        # Pick best move among legal moves.
        if best is None or move_val[0] > best[0] or (move_val[0] == best[0] and (dx, dy) < best[1]):
            best = (move_val[0], (dx, dy))

    return [best[1][0], best[1][1]]