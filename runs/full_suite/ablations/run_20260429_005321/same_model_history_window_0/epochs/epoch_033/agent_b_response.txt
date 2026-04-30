def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((a, b) for a, b in observation["obstacles"])
    resources = observation["resources"]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        # Go toward center while keeping some distance from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny): 
                continue
            dcent = cheb(nx, ny, cx, cy)
            dopp = cheb(nx, ny, ox, oy)
            score = dcent - 0.3 * dopp
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [int(best[1]), int(best[2])] if best else [0, 0]

    best_res = None
    best_val = None
    for rx, ry in resources:
        ds = cheb(x, y, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources you can reach sooner than opponent; also consider being farther behind as penalty
        val = ds - 0.65 * do
        if best_val is None or val < best_val:
            best_val = val
            best_res = (rx, ry)

    tx, ty = best_res

    best = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if nx == tx and ny == ty:
            return [dx, dy]
        dself = cheb(nx, ny, tx, ty)
        dopp = cheb(nx, ny, ox, oy)
        # If opponent is close, prioritize maintaining distance while still moving toward target
        opp_term = 0.0
        if dopp <= 2:
            opp_term = 0.8 * (3 - dopp)
        score = dself + opp_term
        if best is None or score < best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])] if best else [0, 0]