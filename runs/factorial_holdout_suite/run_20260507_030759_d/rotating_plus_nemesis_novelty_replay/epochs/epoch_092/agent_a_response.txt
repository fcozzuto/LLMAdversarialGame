def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target we are likely to arrive at earlier (or tie), with deterministic tie-breaks.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer winning races: maximize (do - ds). If tied, prefer smaller ds, then stable ordering.
        key = (-(do - ds), ds, (rx + 3 * ry) % 97)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Greedy local move toward target; avoid obstacles if possible.
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_md = None
    # Deterministic tie-break preference: prioritize diagonal, then straight, then stay.
    pref = {(-1, -1):0, (0, -1):1, (1, -1):2, (-1, 0):3, (0, 0):6, (1, 0):4, (-1, 1):5, (0, 1):7, (1, 1):8}
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # If we cannot beat the opponent to this target, add slight bias to move sideways (shadow-like traps).
        do = cheb(ox, oy, tx, ty)
        side_bias = 0
        if do <= cheb(sx, sy, tx, ty):
            if dx != 0 and dy == 0:
                side_bias = 1
            elif dx == 0 and dy != 0:
                side_bias = 1
        md = (d + side_bias, pref[(dx, dy)], abs(nx - tx) + abs(ny - ty))
        if best_md is None or md < best_md:
            best_md = md
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]