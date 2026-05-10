def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    self_role = observation.get("self_role", "pursuer") or "pursuer"
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def obst_pen(nx, ny):
        # penalize proximity to obstacles (more weight on immediate adjacency)
        pen = 0
        for (px, py) in obstacles:
            d = cheb(nx, ny, px, py)
            if d == 0: pen += 10
            elif d == 1: pen += 4
            elif d == 2: pen += 1
        return pen

    best = None
    best_val = None

    is_evader = "evader" in self_role
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        # If roles swapped (we act as evader), run away; otherwise chase/intercept.
        if is_evader:
            val = (d_opp, -obst_pen(nx, ny), -nx, -ny)  # maximize distance from pursuer
        else:
            # Prefer smaller distance; tie-break by lower obstacle penalty and being closer to opponent's "direction"
            dirx = 0 if ox == x else (1 if ox > x else -1)
            diry = 0 if oy == y else (1 if oy > y else -1)
            aim = -(abs(nx - (ox)) + abs(ny - (oy)))  # deterministic tie-break
            val = (-d_opp, -obst_pen(nx, ny), aim, nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]