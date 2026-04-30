def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        bestv = -10**18; best = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty) - 0.05 * cheb(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    bestv = -10**18; best = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        mypos = (nx, ny)
        v = -10**18
        for r in resources:
            rx, ry = r[0], r[1]
            if not inb(rx, ry): 
                continue
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources I can reach earlier; slight tie to move toward nearer resources.
            score = (d_op - d_me) * 3.0 - d_me * 0.15
            if score > v:
                v = score
        # Small bias to reduce distance to opponent to deny (deterministic, mild).
        v -= 0.02 * cheb(nx, ny, ox, oy)
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v; best = (dx, dy)
    return [best[0], best[1]]