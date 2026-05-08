def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
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

    # Pick a target we can reach at least as fast as opponent, with preference for closeness to us.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Maximize how far ahead we are; if tie, minimize our distance; then prioritize nearer resources overall.
        key = (od - sd, -sd, - (sd + od))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    raw_dx = 0 if tx == sx else (1 if tx > sx else -1)
    raw_dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Candidate moves: try best-aligned directions first, then alternatives.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                align = -((dx - raw_dx) * (dx - raw_dx) + (dy - raw_dy) * (dy - raw_dy))
                # Choose move that reduces our distance to target, while keeping ahead of opponent.
                nds = cheb(nx, ny, tx, ty)
                ndo = cheb(ox, oy, tx, ty)
                ahead = ndo - nds
                candidates.append(((ahead, -nds, align), [dx, dy]))
    candidates.sort(key=lambda z: z[0], reverse=True)
    return candidates[0][1] if candidates else [0, 0]