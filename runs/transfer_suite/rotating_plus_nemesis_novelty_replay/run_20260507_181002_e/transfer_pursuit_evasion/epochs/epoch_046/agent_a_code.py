def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    sr = str(observation.get("self_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr)
    if not self_is_evader:
        orr = str(observation.get("opponent_role", "")).lower()
        if ("evader" in orr) or ("runner" in orr):
            self_is_evader = False

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]

    if self_is_evader:
        # Prefer moving away from pursuer, but also toward the corner farthest from it.
        best = None
        best_sc = -10**18
        # Pick a single target corner deterministically: farthest from opponent (tie by lexicographic)
        tx, ty = max(corners, key=lambda c: (man(c[0], c[1], ox, oy), -c[0], -c[1]))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d_away = man(nx, ny, ox, oy)
            toward_corner = -man(nx, ny, tx, ty)
            # Small bias toward staying away from the opponent's side (reduce chance of immediate corner trap)
            edge_bias = (nx in (0, w - 1)) * 0.05 + (ny in (0, h - 1)) * 0.05
            sc = d_away * 10 + toward_corner + edge_bias
            if sc > best_sc:
                best_sc = sc
                best = [dx, dy]
        return best if best is not None else [0, 0]

    # Pursuer: greedy chase, tie-break by moving toward center to cut off escapes.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        # If capture occurs (d==0), this dominates.
        center = -(abs(nx - cx) + abs(ny - cy))
        sc = (-d) * 100 + center
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    return best if best is not None else [0, 0]