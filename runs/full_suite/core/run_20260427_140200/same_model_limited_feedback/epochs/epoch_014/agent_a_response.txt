def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def best_dist(px, py):
        if not resources:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dx, dy = px - cx, py - cy
            return dx*dx + dy*dy
        md = None
        for rx, ry in resources:
            d = (px - rx)*(px - rx) + (py - ry)*(py - ry)
            if md is None or d < md:
                md = d
        return md
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = best_dist(nx, ny)
        opdx, opdy = nx - ox, ny - oy
        opd = opdx*opdx + opdy*opdy
        # Prefer closer to resources; break ties by farther from opponent; then deterministic tie on move.
        key = (myd, -opd, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1] if best is not None else [0, 0]