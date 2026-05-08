def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    dirs.append((0, 0))

    def legal_from(x, y):
        out = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                out.append((dx, dy))
        return out if out else [(0, 0)]

    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    def corner_score(cx, cy):
        d2 = (ox - cx) * (ox - cx) + (oy - cy) * (oy - cy)
        return d2
    target_corner = min(corners, key=lambda c: corner_score(c[0], c[1]))
    tx, ty = target_corner

    opp_moves = legal_from(ox, oy)
    my_moves = legal_from(sx, sy)

    def dist2(a, b, c, d):
        return (a - c) * (a - c) + (b - d) * (b - d)

    best = None
    best_val = None

    for mdx, mdy in my_moves:
        nsx, nsy = sx + mdx, sy + mdy
        # Opponent greedy evasion: choose move maximizing distance to us.
        # Small tie-break: also prefer getting closer to predicted corner.
        best_opp = None
        best_opp_val = None
        for odx, ody in opp_moves:
            nox, noy = ox + odx, oy + ody
            d2 = dist2(nsx, nsy, nox, noy)
            corner_d2 = dist2(tx, ty, nox, noy)
            val = (d2, -corner_d2)  # maximize d2, then maximize -corner_d2 (i.e., minimize corner distance)
            if best_opp is None or val > best_opp_val:
                best_opp_val = val
                best_opp = (odx, ody, nox, noy)
        nox, noy = best_opp[2], best_opp[3]
        # Minimax: minimize opponent's best achievable distance to us after simultaneous move.
        worst_dist2 = dist2(nsx, nsy, nox, noy)
        # Tie-break: prefer moving toward predicted corner.
        my_corner_d2 = dist2(tx, ty, nsx, nsy)
        key = (worst_dist2, my_corner_d2)
        if best is None or key < best_val:
            best_val = key
            best = (mdx, mdy)

    return [int(best[0]), int(best[1])]