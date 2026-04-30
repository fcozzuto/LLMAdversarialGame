def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def score_pos(px, py):
        # Higher is better: prioritize being closer than opponent to a resource.
        best = -10**18
        for rx, ry in resources:
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Strongly prefer winning (ds < do); also prefer capturing nearer resources.
            win = (do - ds)
            v = win * 30 - ds
            if v > best:
                best = v
        # Additional safety: avoid letting opponent close significantly to their best resource.
        # (Approximate by penalizing proximity to opponent position when we're not closer to any resource.)
        return best - (cheb(px, py, ox, oy) if best < 0 else 0)

    moves = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            candidates.append((dx, dy, score_pos(nx, ny), cheb(nx, ny, ox, oy)))
    if not candidates:
        return [0, 0]

    # Deterministic tie-break: max score, then farthest from opponent to reduce their capture rate, then smallest dx/dy order.
    candidates.sort(key=lambda t: (t[2], t[3] * 0 + 0, -t[3], t[0], t[1]))
    # Above sort line has redundant part; keep deterministic: re-sort with explicit keys.
    candidates.sort(key=lambda t: (-t[2], t[3], t[0], t[1]))
    return [int(candidates[0][0]), int(candidates[0][1])]