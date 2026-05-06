def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles
    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): continue
            d = md(nx, ny, tx, ty)
            key = (d, dx, dy)
            if best is None or key < best[0]: best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Prefer a move that creates the largest distance advantage over the opponent for a contested resource.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny): continue
        # Use best contest among reachable resources from this next position
        best_m = -10**9
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # If we are closer, this is good; if not, still consider reducing opponent's lead.
            # Add slight preference for nearer self progress.
            m = (do - ds) * 10 - ds
            if m > best_m: best_m = m
        # Secondary: avoid heading toward opponent directly unless it helps contesting.
        opp_d = md(nx, ny, ox, oy)
        key = (-best_m, opp_d, dx, dy)
        if best is None or key < best[0]: best = (key, dx, dy)
    return [best[1], best[2]] if best else [0, 0]