def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # sweep_rows opponent heuristic: penalize resources on opponent's current row
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        ahead = od - sd  # positive if we arrive earlier
        same_row_pen = 3 if ry == oy else 0
        near_opp_pen = 0 if od >= sd else 1  # closer to opponent than us
        # Prefer: be ahead, then closer to us, then avoid opponent row
        key = (-(ahead), sd + same_row_pen + near_opp_pen, od, rx + ry, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    tx, ty = best[1], best[2]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = cheb(nx, ny, tx, ty)
                # also discourage stepping into opponent-favored row if not needed
                row_pen = 2 if ny == oy and ty != oy else 0
                moves.append((d + row_pen, cheb(nx, ny, ox, oy), dx, dy))
    moves.sort()
    return [int(moves[0][2]), int(moves[0][3])]