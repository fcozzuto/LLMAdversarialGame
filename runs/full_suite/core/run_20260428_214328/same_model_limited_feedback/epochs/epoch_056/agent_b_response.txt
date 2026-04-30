def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [7, 7])
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    # Chebyshev distance (diagonal allowed)
    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Candidate move validity
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def valid(nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return False
        return (nx, ny) not in obstacles

    if not resources:
        # If no visible resources, move away from opponent slightly to reduce collision potential
        dx = 0 if ox == sx else (1 if ox < sx else -1)
        dy = 0 if oy == sy else (1 if oy < sy else -1)
        nx, ny = sx + (-dx), sy + (-dy)
        for mx, my in moves:
            tx, ty = sx + mx, sy + my
            if valid(tx, ty) and (tx != nx or ty != ny):
                continue
        if valid(nx, ny):
            return [nx - sx, ny - sy]
        # fallback: any valid move
        for mx, my in moves:
            tx, ty = sx + mx, sy + my
            if valid(tx, ty):
                return [mx, my]
        return [0, 0]

    # Choose target resource where we can beat opponent (or at least deny)
    best = None
    bx, by = None, None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d_me = dist((sx, sy), (rx, ry))
        d_op = dist((ox, oy), (rx, ry))
        # Priority: we closer to resource; then closeness; then deterministic tiebreaker
        # Slightly prefer resources also far from opponent (deny) if tie.
        score = (0 if d_me <= d_op else 1, d_me - d_op, d_me, rx, ry)
        if best is None or score < best:
            best = score
            bx, by = rx, ry

    # Move toward chosen target while avoiding obstacles
    tx, ty = bx, by
    best_move = None
    best_eval = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        # Evaluation: distance to target; if equal, prefer reducing opponent distance to same target (deny)
        d1 = dist((nx, ny), (tx, ty))
        d2 = dist((ox, oy), (tx, ty))  # current opponent-to-target (constant), but used for tie-breaking
        # Also bias against getting too close to opponent to avoid mutual blocking.
        opp_close = dist((nx, ny), (ox, oy))
        eval_key = (d1, opp_close, -d2, mx, my, nx, ny)
        if best_eval is None or eval_key < best_eval:
            best_eval = eval_key
            best_move = (mx, my)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]