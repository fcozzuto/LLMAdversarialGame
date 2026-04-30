def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        cx, cy = (w - 1) / 2, (h - 1) / 2
        moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]+[(0, 0)]
        def ok(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            d_op = max(abs(nx - ox), abs(ny - oy))
            d_c = max(abs(nx - cx), abs(ny - cy))
            sc = d_op + 0.1 * d_c
            if sc > best[1]:
                best = ((dx, dy), sc)
        return list(best[0] if best[0] is not None else (0, 0))
    def dist(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]+[(0, 0)]
    def ok(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    # Choose target resource by score: prefer ones we can reach sooner than opponent
    best_res = None
    best_key = -10**18
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        key = (do - ds) * 1000 - ds
        # slight bias to closer resources when contested similarly
        key += -abs((rx - (w-1)/2)) * 0.01 - abs((ry - (h-1)/2)) * 0.01
        if key > best_key:
            best_key = key
            best_res = (rx, ry)
    rx, ry = best_res
    # Move selection: greedy toward target, avoid obstacles, discourage moving closer to opponent
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny): 
            continue
        ds_new = dist(nx, ny, rx, ry)
        do_new = dist(nx, ny, ox, oy)
        # Main: decrease distance to target; Secondary: increase distance from opponent
        score = -ds_new * 10 + do_new * 1.0
        # Tiebreak deterministically: prefer diagonal/forward over staying
        score += (1 if dx != 0 and dy != 0 else 0) * 0.01
        score += (0 if (dx == 0 and dy == 0) else 0.001)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]