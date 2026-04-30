def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or []) if r is not None]
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return x < 0 or y < 0 or x >= w or y >= h or (x, y) in obstacles

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not blocked(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Target bias: move toward nearest resource, but never allow opponent to "cut off" too cheaply.
    best = None
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        # Immediate grab
        val = 0
        if (nx, ny) in obstacles:
            val -= 100000
        if (nx, ny) in resources:
            val += 5000

        # Distance to closest resource
        dR = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        val -= 120 * dR

        # Opponent influence: penalize moves that reduce our advantage or let them be close.
        dO = cheb(nx, ny, ox, oy)
        if dO == 0:
            val -= 100000
        else:
            val -= 25 * (3 - dO if dO < 3 else 0)
            val += 8 * dO

        # Competitive "race": compare our distance to nearest resource vs opponent's.
        my_best = min(cheb(sx, sy, rx, ry) for rx, ry in resources)
        opp_best = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
        # If we're far behind, prioritize cutting distance quickly.
        if my_best - opp_best > 0:
            val -= 40 * (dR - my_best)
        else:
            val -= 12 * dR

        # Encourage staying off obstacles' near-field (cheap local avoidance)
        if obstacles:
            near = min(cheb(nx, ny, px, py) for px, py in obstacles)
            if near <= 1:
                val -= 60
            elif near == 2:
                val -= 15

        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]