def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0]); ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy

    # Prefer moves that (1) immediately reduce threat resources opponent can grab, (2) collect nearby resources.
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = (None, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # If landing on a resource, strong bias.
        on_res = 1 if (nx, ny) in resources else 0
        val = on_res * 100000
        # Look for a resource to "steal": where opponent is closer or tie.
        # Also include general progress toward the closest reachable resource.
        progress = 0
        steal = 0
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            dself = cheb(sx, sy, rx, ry)
            # improvement toward it
            progress += (dself - ds)
            # steal priority if opponent currently closer or equal
            if do <= ds:
                # bigger when opponent is much closer or when it's soon for us
                steal += (do - ds) * 2 + (10 - ds)
        # Penalize getting too close to edges/obstacle wells a bit (deterministic tie-breaker).
        edge_pen = (1 if nx == 0 or nx == w - 1 else 0) + (1 if ny == 0 or ny == h - 1 else 0)
        val += progress * 5 + steal * 3 - edge_pen
        # Deterministic tie-breaker: prefer smaller dx, then smaller dy, then staying
        if val > best[1] or (val == best[1] and (dx, dy) < best[0]):
            best = ((dx, dy), val)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]