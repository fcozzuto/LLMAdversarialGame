def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    # Endgame: maximize distance from opponent deterministically
    if not resources or observation.get("remaining_resource_count", len(resources)) <= 0:
        best = None; bestm = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, ox, oy)
            key = (d, -abs(nx - sx) - abs(ny - sy), nx, ny)
            if best is None or key > best:
                best = key; bestm = [dx, dy]
        return bestm if valid(sx, sy) else [0, 0]

    # Target selection: prefer resources where we are relatively closer than opponent (intercept goal)
    best_t = None
    best_adv = -10**9
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = (od - sd)  # higher means we can arrive earlier
        # Break ties toward nearer resources to commit faster
        key = (adv, -(sd), -(rx + ry))
        if best_t is None or key > best_adv_key:
            best_adv_key = key
            best_t = (rx, ry)
            best_adv = adv

    tx, ty = best_t

    # Move evaluation: go toward chosen target but also avoid letting opponent close gap on it
    best = None; bestm = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        # If opponent is closer than us, bias to reduce our distance faster; else maintain lead
        need = 1.0 if od2 > sd2 else 0.0
        lead = (od2 - sd2)
        # Also slightly reduce distance between us and target compared to current, to make meaningful progress
        prog = (cheb(sx, sy, tx, ty) - sd2)
        # Obstacle/terrain proxy: lightly prefer moves that increase distance from opponent to reduce contention
        cont = cheb(nx, ny, ox, oy)
        key = (lead, prog, -need, cont, -abs(nx - tx) - abs(ny - ty), nx, ny)
        if best is None or key > best:
            best = key; bestm = [dx, dy]

    return bestm if valid(sx + bestm[0], sy + bestm[1]) else [0, 0]