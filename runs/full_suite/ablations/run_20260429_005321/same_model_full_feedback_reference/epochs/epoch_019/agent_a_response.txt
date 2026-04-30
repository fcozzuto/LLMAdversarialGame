def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Fallback if no resources
    if not resources:
        tx, ty = (w - 1, h - 1) if (sx, sy) == (0, 0) else (ox, oy)
    else:
        # Prefer resources where we are not too far behind opponent; tie-break deterministically.
        best = None
        best_key = None
        for rx, ry in resources:
            d1 = md(sx, sy, rx, ry)
            d2 = md(ox, oy, rx, ry)
            behind = d1 - d2  # negative means we are closer
            # Encourage moving toward resources; discourage long detours; slight bias to center.
            center_bias = -abs(rx - (w - 1) / 2.0) - abs(ry - (h - 1) / 2.0)
            key = (behind, d1, -center_bias, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    # Also mildly prefer staying away from opponent to avoid collisions/being blocked.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Score: reduce distance to target; avoid opponent; slight center pull.
        cur = md(nx, ny, tx, ty)
        oppd = md(nx, ny, ox, oy)
        center = -abs(nx - (w - 1) / 2.0) - abs(ny - (h - 1) / 2.0)
        # If opponent can grab the same resource sooner, prioritize increasing opp distance.
        dtx_cur = cur
        dtx_opp = md(ox, oy, tx, ty)
        block_term = 0
        if dtx_cur > dtx_opp:
            block_term = (oppd) * 0.08
        score = (cur, -oppd, -center, -block_term, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]