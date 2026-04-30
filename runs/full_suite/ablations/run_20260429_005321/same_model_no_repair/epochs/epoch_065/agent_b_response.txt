def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_pen(x, y):
        if not inb(x, y): return 10**7
        if (x, y) in obstacles: return 10**6
        p = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0: 
                    continue
                if (x + ddx, y + ddy) in obstacles:
                    p += 4
        return p

    def best_resource_score(px, py):
        if not resources: 
            return -10**18, None
        best_s = -10**30
        best_r = None
        for rx, ry in resources:
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we are closer to; also prefer reducing our distance
            s = (do - ds) * 120 - ds
            # If very close to a resource, prioritize hard
            if ds == 0: s += 10**6
            # Small deterministic tie-breaker
            if (do - ds, -ds, -rx, -ry) > (best_s, 0, -10**9, -10**9):
                pass
            if s > best_s or (s == best_s and (rx, ry) < best_r):
                best_s, best_r = s, (rx, ry)
        return best_s, best_r

    # Two-phase: pick the best target from current position, then choose the move that best improves it.
    _, target = best_resource_score(sx, sy)
    if target is None:
        # No resources: just avoid obstacles and drift toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        best_v = -10**30
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -cheb(nx, ny, tx, ty) - obst_pen(nx, ny)
            if v > best_v:
                best_v = v
                best = (dx, dy)
        return [best[0], best[1]]

    tx, ty = target
    best_move = (0, 0)
    best_val = -10**30

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        ds_new = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)

        # Extra: avoid giving opponent a better winning line by also scoring for their distance changes
        # (1-step heuristic using target only to keep deterministic and fast)
        val = (do - ds_new) * 140 - ds_new - obst_pen(nx, ny)

        # If we are not closer to the target after moving, slightly penalize (prevents oscillation)
        if ds_new > cheb(sx, sy, tx, ty):
            val -= 25

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]