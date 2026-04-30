def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Prefer resources where we are strictly closer (or tie and closer to get there by next step).
    def score_cell(nx, ny, rx, ry):
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If opponent can reach sooner or equally, devalue heavily.
        rel = do - ds
        if rel <= 0:
            return -1000 + rel * 5 - ds
        # If we're closer, prefer near and also "deny" by keeping opponent far.
        return rel * 20 + (40 - ds) + (do - ds) * 2

    if resources:
        best = None  # (value, tie_key, dx, dy)
        for dx, dy, nx, ny in legal:
            # Evaluate best resource from this potential next position.
            vbest = float("-inf")
            tie = 0
            for i, (rx, ry) in enumerate(resources):
                v = score_cell(nx, ny, rx, ry)
                if v > vbest:
                    vbest = v
                    tie = i
            # Tie-break deterministically: prefer moves that increase distance from opponent (denial),
            # then prefer smaller lexicographic move.
            opp_denial = cheb(nx, ny, ox, oy)
            key = (-opp_denial, dx, dy, tie)
            cand = (vbest, key, dx, dy)
            if best is None or cand > best:
                best = cand
        return [int(best[2]), int(best[3])]

    # No resources: move to reduce chance opponent takes future resources by heading toward center.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy, nx, ny in legal:
        v = cheb(nx, ny, cx, cy)  # minimize
        tie = (cheb(nx, ny, ox, oy), -dx, -dy)
        cand = (-v, tie, dx, dy)
        if best is None or cand > best:
            best = cand
    return [int(best[2]), int(best[3])]