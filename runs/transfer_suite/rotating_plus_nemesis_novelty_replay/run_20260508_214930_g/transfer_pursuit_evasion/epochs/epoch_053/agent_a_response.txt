def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    cap = int(observation.get("capture_radius", 0) or 0)
    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                m += 1
        return m

    # Target heuristic: chase opponent, but if far, bias toward the farthest corner from opponent to limit zigzags.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    dist_to_opp = cheb(sx, sy, ox, oy)
    use_corner_bias = 1 if dist_to_opp >= 3 else 0
    tx, ty = (far_corner[0], far_corner[1]) if use_corner_bias else (ox, oy)

    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_tar = cheb(nx, ny, tx, ty)
        m = mobility(nx, ny)
        # Key: prioritize capture, then minimize distance to opponent; add small penalties to avoid low-mobility moves.
        cap_flag = 0 if (cap and d_opp <= cap) else 1
        key = (cap_flag, d_opp, d_tar, -m, dx * 3 + dy)  # deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]