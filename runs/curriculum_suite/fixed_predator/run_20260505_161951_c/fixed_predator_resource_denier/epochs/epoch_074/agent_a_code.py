def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w - 1, h - 1
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty) - cheb(nx, ny, ox, oy)*0.1
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    best = [0, 0]; bestv = -10**18
    # One-step deterministic lookahead: maximize expected "capture advantage" over all known resources.
    # Advantage is larger when we can get to the resource sooner than the opponent.
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        v = 0
        for rx, ry in resources:
            ourd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            adv = oppd - ourd
            # Favor moves that create strong lead; slightly penalize long travel.
            v += adv * 120 - ourd * 3
        # Add a small pressure term to not run directly away from the closest opponent threat.
        # (choose the resource where opponent is currently closest)
        threat = 10**9
        for rx, ry in resources:
            t = cheb(ox, oy, rx, ry)
            if t < threat:
                threat = t
        v -= cheb(nx, ny, ox, oy) * 1.5
        if v > bestv:
            bestv = v; best = [dx, dy]
    return best