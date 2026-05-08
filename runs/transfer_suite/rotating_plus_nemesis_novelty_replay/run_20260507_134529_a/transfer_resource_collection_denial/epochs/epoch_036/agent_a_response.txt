def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def eval_move(nx, ny):
        if not free(nx, ny):
            nx, ny = sx, sy
        if not resources:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            return -(cheb(nx, ny, cx, cy))
        best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Main: win/contest resource (prefer larger advantage)
            adv = do - ds
            # Secondary: be closer if tied or uncertain; also prefer moving away from opponent too
            clos = -ds
            ant = cheb(nx, ny, rx, ry) - cheb(ox, oy, rx, ry)
            val = adv * 1000 + clos * 5 - ant * 2
            if val > best:
                best = val
        # Small preference to reduce distance to "best" resource overall
        # (deterministic and cheap: minimize cheb to the resource we're currently most likely to beat)
        best_ds = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if do - ds > 0:
                if ds < best_ds:
                    best_ds = ds
        if best_ds < 10**9:
            best += -best_ds
        return best

    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-break by fixed dir order
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = eval_move(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx if inb(nx, ny) else 0, dy if inb(nx, ny) else 0)
    return [best_move[0], best_move[1]]