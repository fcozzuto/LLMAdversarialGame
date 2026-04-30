def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def legal(x, y): return inb(x, y) and (x, y) not in obs_set

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # Choose a target resource: strongly prefer those where we are closer than opponent.
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer winning races; if none, prefer closest with some safety from opponent.
        key = ((od - sd), -(sd + 2*cheb(ox, oy, rx, ry)), -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]

    tx, ty = best[1]

    # If opponent is too close, temporarily bias to retreat/avoid direct competition.
    d_opp = cheb(sx, sy, ox, oy)
    retreat = d_opp <= 2

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dres = cheb(nx, ny, tx, ty)
        dopp = cheb(nx, ny, ox, oy)
        # Main: minimize distance to target.
        # Secondary: maximize distance from opponent (especially when retreating).
        val = (-(dres), dopp if retreat else dopp//2, -abs(nx - tx) - abs(ny - ty), -nx, -ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]