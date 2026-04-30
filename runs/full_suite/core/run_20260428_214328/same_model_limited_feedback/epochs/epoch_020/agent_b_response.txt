def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b, c, d): 
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        best = (10**9, -10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                dself = cheb(nx, ny, ox, oy)
                cand = (-(dself), 0, dx, dy)
                if cand < best:
                    best = cand
        return [best[2], best[3]]
    best_val = -10**9
    best_resources = []
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        val = do - ds
        if val > best_val:
            best_val = val
            best_resources = [(rx, ry, ds)]
        elif val == best_val:
            best_resources.append((rx, ry, ds))
    tr, ty, _ = min(best_resources, key=lambda t: (t[2], abs(t[0]-sx)+abs(t[1]-sy), t[0], t[1]))
    best = (10**9, -10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dtar = cheb(nx, ny, tr, ty)
        dop = cheb(nx, ny, ox, oy)
        landed = (nx == tr and ny == ty)
        # Prefer landing; otherwise minimize distance to target, then maximize distance from opponent, then tie-break.
        cand = (0 if landed else dtar, -dop, dx, dy)
        if cand < best:
            best = cand
    return [best[2], best[3]]