def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def sgn(v):
        return (v > 0) - (v < 0)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Filter resources to valid cells
    vals = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if cell_ok(x, y):
                vals.append((x, y))
    if not vals:
        return [0, 0]

    # Choose target: maximize our distance advantage; tie-break by nearer resource to center-ish
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    best_key = None
    for tx, ty in vals:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv = opd - myd
        center_bias = -cheb(tx, ty, cx, cy)
        key = (adv, center_bias, -(myd + opd))
        if best is None or key > best_key:
            best, best_key = (tx, ty), key
    tx, ty = best

    myd = cheb(sx, sy, tx, ty)
    opd = cheb(ox, oy, tx, ty)

    # If opponent is closer, try to contest by moving toward the step between opponent and target.
    if opd <= myd:
        step_x = ox + sgn(tx - ox)
        step_y = oy + sgn(ty - oy)
        if cell_ok(step_x, step_y):
            aim_x, aim_y = step_x, step_y
        else:
            aim_x, aim_y = tx, ty
    else:
        aim_x, aim_y = tx, ty

    # Score candidate moves
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        # Prefer closer to aim; lightly avoid allowing opponent to get closer too much.
        d_to_aim = cheb(nx, ny, aim_x, aim_y)
        d_opp_to_target = cheb(ox, oy, tx, ty)
        d_opp_to_next = cheb(ox, oy, nx, ny)
        # Also avoid moving adjacent into opponent when we're already behind.
        danger = 0
        if opd <= myd:
            danger = -cheb(nx, ny, ox, oy)
        score = (-d_to_aim * 1000) + (-(d_opp_to_target) * 0.1) + (d_opp_to_next * -0.01) + danger
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]