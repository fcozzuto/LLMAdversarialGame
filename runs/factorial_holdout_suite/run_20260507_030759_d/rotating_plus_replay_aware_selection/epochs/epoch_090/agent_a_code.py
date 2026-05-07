def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if w <= 0 or h <= 0:
        return [0, 0]

    if not resources:
        return [0, 0]

    # Select a resource we can reach earlier (deterministic tie-breaks).
    best_r = None
    best_margin = -10**9
    best_own = 10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d_own = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        margin = d_opp - d_own
        # Prefer positive margin; tie-break by smaller d_own then by coordinates.
        if (margin > best_margin) or (margin == best_margin and (d_own < best_own or (d_own == best_own and (rx, ry) < best_r))):
            best_margin = margin
            best_own = d_own
            best_r = (rx, ry)

    rx, ry = best_r
    if sx == rx and sy == ry:
        return [0, 0]

    # Choose move maximizing post-move capture margin; if equal, minimize own dist.
    best_move = (0, 0)
    best_val = -10**18
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not legal(nx, ny):
            continue
        d_own2 = cheb(nx, ny, rx, ry)
        d_opp2 = cheb(ox, oy, rx, ry)
        margin2 = d_opp2 - d_own2
        # Small deterministic bias to break ties toward increasing x then y.
        bias = nx * 0.001 + ny * 0.000001
        val = margin2 * 1000 - d_own2 + bias
        if val > best_val:
            best_val = val
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]