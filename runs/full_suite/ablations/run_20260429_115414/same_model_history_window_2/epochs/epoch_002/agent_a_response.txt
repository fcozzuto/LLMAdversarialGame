def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def sign(v):
        return 0 if v == 0 else (-1 if v < 0 else 1)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_score = -10**18

    if not resources:
        # drift toward center to reduce predictability
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        dx = sign(tx - sx)
        dy = sign(ty - sy)
        for mx, my in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            nx, ny = sx + mx, sy + my
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [mx, my]
        return [0, 0]

    # Pick a target resource where we are relatively closer than the opponent.
    best_t = None
    best_adv = -10**18
    best_sd = 10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd0 = cheb(sx, sy, rx, ry)
        od0 = cheb(ox, oy, rx, ry)
        adv = od0 - sd0
        if adv > best_adv or (adv == best_adv and (sd0 < best_sd or (sd0 == best_sd and (rx, ry) < best_t))):
            best_adv = adv
            best_sd = sd0
            best_t = (rx, ry)

    rx, ry = best_t
    # Score each candidate by improving our distance to the target and (secondarily) worsening theirs.
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd1 = cheb(nx, ny, rx, ry)
        od1 = cheb(ox, oy, rx, ry)  # opponent position unchanged this turn
        # Encourage reaching the target quickly; deter letting opponent be as close.
        score = (best_adv + (od1 - sd1)) * 10 - sd1
        # Small tie-breaker: prefer moves that also increase distance from opponent to avoid contested pickups.
        score += 0.1 * cheb(nx, ny, ox, oy)
        if score > best_score or (score == best_score and (mx, my) < best_move):
            best_score = score
            best_move = (mx, my)

    return [best_move[0], best_move[1]]