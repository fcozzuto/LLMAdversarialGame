def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if sx == ox and sy == oy:
        return [0, 0]

    my_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            my_moves.append((nx, ny, dx, dy))
    if not my_moves:
        return [0, 0]

    ev_moves = []
    for dx, dy in deltas:
        nx, ny = ox + dx, oy + dy
        if legal(nx, ny):
            ev_moves.append((nx, ny, dx, dy))
    if not ev_moves:
        return [0, 0]

    best = None
    # Minimax: choose move that minimizes worst-case distance after both move.
    # Tie-break: prefer smaller current distance and slight "alignment" toward evader.
    for nx, ny, dx, dy in my_moves:
        worst = -1
        best_ev_guarantee = None
        for ex, ey, _, _ in ev_moves:
            if nx == ex and ny == ey:
                d = -10**18  # immediate capture preferred
            else:
                d = dist2(nx, ny, ex, ey)
            if d > worst:
                worst = d
                best_ev_guarantee = ex + ey  # deterministic, unused except tie
        cur_d = dist2(nx, ny, ox, oy)
        align = abs(nx - ox) + abs(ny - oy)
        key = (worst, cur_d, align, nx, ny)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1]