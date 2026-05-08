def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def clamp_move(x, y, tx, ty):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        nx, ny = x + dx, y + dy
        if free(nx, ny):
            return (nx, ny)
        # If blocked, try axis-aligned alternatives deterministically
        candidates = [(x + dx, y), (x, y + dy), (x, y), (x - dx, y), (x, y - dy)]
        for cx, cy in candidates:
            if free(cx, cy):
                return (cx, cy)
        return (x, y)

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Predict opponent's move under pursuit_direct-like behavior (greedy toward our next position)
    turn_index = int(observation.get("turn_index", 0) or 0)
    best = None  # (score, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Candidate predicted opponent positions: toward our next position and slight alternation to break ties
        pred1 = clamp_move(ox, oy, nx, ny)
        # deterministic tie-breaking variant: if equal Manhattan step, choose perpendicular bias by turn parity
        if turn_index % 2 == 0:
            pred2 = clamp_move(ox, oy, nx, ny - 1 if ny - 1 >= 0 else ny)
        else:
            pred2 = clamp_move(ox, oy, nx - 1 if nx - 1 >= 0 else nx, ny)

        dmin = min(dist2(pred1[0], pred1[1], nx, ny), dist2(pred2[0], pred2[1], nx, ny))

        # Additional heuristic: prefer moves that increase distance from current opponent and avoid cornering
        dcur = dist2(sx, sy, ox, oy)
        edge_pen = (nx == 0 or nx == w - 1) + (ny == 0 or ny == h - 1)
        score = dmin + 0.1 * (dcur) - 0.05 * edge_pen

        if best is None or score > best[0] + 1e-12 or (abs(score - best[0]) <= 1e-12 and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    if best is None:
        # Fallback deterministic safe move toward farthest corner
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        target = max(corners, key=lambda c: dist2(sx, sy, c[0], c[1]))
        return [0 if target[0] == sx else (1 if target[0] > sx else -1),
                0 if target[1] == sy else (1 if target[1] > sy else -1)]

    return [int(best[1]), int(best[2])]