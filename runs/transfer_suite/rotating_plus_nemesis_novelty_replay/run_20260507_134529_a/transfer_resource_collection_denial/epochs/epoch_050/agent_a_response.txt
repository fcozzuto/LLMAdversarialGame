def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_dx, best_dy, best_val = 0, 0, -10**18

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        candidates.append((nx, ny, dx, dy))

    if not resources:
        for nx, ny, dx, dy in candidates:
            v = cheb(nx, ny, ox, oy)
            if v > best_val:
                best_val = v
                best_dx, best_dy = dx, dy
        return [int(best_dx), int(best_dy)]

    for nx, ny, dx, dy in candidates:
        self_min = 10**9
        val = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if sd < self_min:
                self_min = sd
            gap = od - sd  # positive: we are closer
            cand = gap * 100 - sd * 2
            if cand > val:
                val = cand
        # Ensure we also generally keep progressing even if all gaps are negative
        val += -self_min
        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]