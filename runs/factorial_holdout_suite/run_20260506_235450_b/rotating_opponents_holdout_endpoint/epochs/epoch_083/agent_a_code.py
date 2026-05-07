def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = set()
    for ob in obstacles:
        if isinstance(ob, (list, tuple)) and len(ob) >= 2:
            obs_set.add((int(ob[0]), int(ob[1])))

    endgame = int(observation.get("remaining_resource_count", 999) or 999) <= 5

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Pick best target: maximize (opp_dist - self_dist), then smaller self_dist, then closer to opponent corner (deterministic tie-break)
    best_r = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # In endgame, prioritize securing nearest remaining resources even if opponent is close.
        adv = od - sd
        if endgame:
            key = (adv, -sd, -cheb(ox, oy, tx, ty))
        else:
            key = (adv, -sd, -cheb(ox, oy, tx, ty))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (tx, ty)

    tx, ty = best_r

    # Choose a move that minimizes distance to the target while avoiding obstacles; tie-break toward reducing our Chebyshev distance.
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        hit = (nx, ny) in obs_set
        # If hit, engine keeps in place; model it by staying.
        if hit:
            nx, ny = sx, sy
        d = cheb(nx, ny, tx, ty)
        sdist = man(nx, ny, tx, ty)
        # Second objective: keep moving in direction that also slightly reduces opponent access to target (approx).
        od = man(ox, oy, tx, ty)
        val = (0 if not hit else 1, d, sdist, - (od - sdist))
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]