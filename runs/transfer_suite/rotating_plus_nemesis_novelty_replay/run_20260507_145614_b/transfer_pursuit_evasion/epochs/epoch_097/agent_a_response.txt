def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obst

    # Opponent model: deterministically choose move that maximizes our distance (tie: prefer staying closer to a corner away from us)
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def opp_move(ex, ey, usx, usy):
        best = None
        best_d = None
        best_corner_bias = None
        for dx, dy in moves:
            nx, ny = ex + dx, ey + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, usx, usy)
            if best_d is None or d > best_d:
                best_d = d
                best = (dx, dy)
                best_corner_bias = min(dist2(nx, ny, cx, cy) for cx, cy in corners)
            elif d == best_d:
                cb = min(dist2(nx, ny, cx, cy) for cx, cy in corners)
                if cb > best_corner_bias:
                    best = (dx, dy)
                    best_corner_bias = cb
        return best if best is not None else (0, 0)

    # Our move: minimax over one opponent step after our move (depth-2 with deterministic opponent)
    best = (0, 0)
    best_worst = None
    tie_bias = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        odx, ody = opp_move(ox, oy, nx, ny)
        nxo, nyo = ox + odx, oy + ody
        worst = dist2(nx, ny, nxo, nyo)
        # tie-break: prefer reducing distance immediately and moving toward center to fight wall-run patterns
        imm = dist2(nx, ny, ox, oy)
        center = ((w - 1) / 2.0, (h - 1) / 2.0)
        cb = dist2(nx, ny, int(center[0]), int(center[1]))
        if best_worst is None or worst < best_worst or (worst == best_worst and (imm < dist2(sx + best[0], sy + best[1], ox, oy) or cb < tie_bias)):
            best_worst = worst
            best = (dx, dy)
            tie_bias = cb

    return [int(best[0]), int(best[1])]