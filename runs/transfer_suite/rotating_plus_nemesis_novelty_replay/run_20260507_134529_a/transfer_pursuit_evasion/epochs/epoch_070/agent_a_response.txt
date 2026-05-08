def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    neigh_obs = [(0,0),(1,0),(-1,0),(0,1),(0,-1)]
    def cell_pen(x, y):
        pen = 0
        for dx, dy in neigh_obs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs: pen += 3
        if (x, y) in obs: pen += 100
        return pen

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_val = None
    # tie-break order: deterministic by iterating moves in fixed order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            val = -10**9 if is_evader else 10**9
        elif (nx, ny) in obs:
            val = -10**9 if is_evader else 10**9
        else:
            d = cheb(nx, ny, ox, oy)
            p = cell_pen(nx, ny)
            # Evader: maximize distance; Pursuer: minimize distance. Obstacles add penalty.
            if is_evader:
                val = (d * 10) - p
            else:
                val = (-d * 10) - p
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val
    return [int(best[0]), int(best[1])]