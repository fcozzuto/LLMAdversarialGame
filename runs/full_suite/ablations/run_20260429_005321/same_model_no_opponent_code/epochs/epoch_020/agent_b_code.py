def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx*dx + dy*dy
    def step_free(nx, ny): return inside(nx, ny) and (nx, ny) not in obst

    def free_neighbors(nx, ny):
        c = 0
        for dxm, dym in moves:
            tx, ty = nx + dxm, ny + dym
            if step_free(tx, ty):
                c += 1
        return c

    def near_obstacle(nx, ny):
        for dxm, dym in moves:
            tx, ty = nx + dxm, ny + dym
            if inside(tx, ty) and (tx, ty) in obst:
                return 1
        return 0

    # Pick best resource to chase: prefer ones we can reach at least as fast as opponent
    best_target = None
    best_margin = -10**18
    for rx, ry in resources:
        if (rx, ry) in obst: 
            continue
        d_self = dist2(x, y, rx, ry)
        d_opp = dist2(ox, oy, rx, ry)
        margin = d_opp - d_self  # positive => we are closer
        # small bias to closer resources and to corners/edges less (deterministic tie-break)
        key = margin * 10000 - d_self
        if key > best_margin:
            best_margin = key
            best_target = (rx, ry)

    # If no resources (or weird), just maximize mobility and keep away from opponent/obstacles
    if not best_target:
        best_score = -10**18
        best_move = [0, 0]
        for dxm, dym in moves:
            nx, ny = x + dxm, y + dym
            if not step_free(nx, ny): 
                continue
            s = free_neighbors(nx, ny) - 0.1*dist2(nx, ny, ox, oy) - 0.7*near_obstacle(nx, ny)
            if s > best_score:
                best_score, best_move = s, [dxm, dym]
        return best_move

    tx, ty = best_target

    # Evaluate immediate moves
    best_score = -10**18
    best_move = [0, 0]
    for dxm, dym in moves:
        nx, ny = x + dxm, y + dym
        if not step_free(nx, ny):
            continue

        d_now = dist2(x, y, tx, ty)
        d_next = dist2(nx, ny, tx, ty)

        # attraction to target
        s = (d_now - d_next) * 3.0

        # if move lands on a resource
        if (nx, ny) in {(r[0], r[1]) for r in resources}:
            s += 50.0

        # avoid opponent when too close; also discourage allowing opponent to converge
        d_opp_next = dist2(nx, ny, ox, oy)
        s += 0.08 * d_opp_next  # generally prefer being farther
        if d_opp_next <= 4:   # within 2 tiles
            s -= 40.0

        # obstacle proximity and mobility
        s += 0.6 * free_neighbors(nx, ny)
        s -= 1.2 * near_obstacle(nx, ny)

        # tie-break deterministically: prefer moves with smaller dx,dy lex order via score then sum
        if s > best_score or (s == best_score and (dxm, dym) < (best_move[0], best_move[1])):
            best_score, best_move = s, [dxm, dym]

    return best_move