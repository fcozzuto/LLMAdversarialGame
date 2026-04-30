def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Select best resource by "advantage" (opp farther than us)
    best = None
    best_adv = None
    best_sd = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        if best is None or adv > best_adv or (adv == best_adv and (sd < best_sd or (sd == best_sd and (rx, ry) < best))):
            best = (rx, ry)
            best_adv = adv
            best_sd = sd

    # If no resources, move to closest available (or stay)
    if best is None:
        return [0, 0]

    tx, ty = best

    # Candidate moves ordered deterministically: toward target, then alternatives
    step_dx = 0
    if tx > sx: step_dx = 1
    elif tx < sx: step_dx = -1
    step_dy = 0
    if ty > sy: step_dy = 1
    elif ty < sy: step_dy = -1

    candidates = []
    # Prefer exact toward-step first, then other moves by fixed priority
    candidates.append((step_dx, step_dy))
    pri = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in pri:
        if (dx, dy) != (step_dx, step_dy):
            candidates.append((dx, dy))

    best_move = (0, 0)
    best_dist = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, tx, ty)
        # Also prefer moves that reduce opponent advantage (more pressure) if equal distance
        opp_dist = cheb(ox, oy, tx, ty)
        my_adv = opp_dist - dist
        if best_dist is None or dist < best_dist or (dist == best_dist and my_adv > (cheb(ox, oy, tx, ty) - cheb(sx, sy, tx, ty))) or (dist == best_dist and (dx, dy) < best_move):
            best_dist = dist
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]