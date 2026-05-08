def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_adv_for_target(tx, ty, ax, ay):
        self_d = cheb(ax, ay, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        return opp_d - self_d  # higher is better for us

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    # If standing on a resource, stop to secure it deterministically.
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    # Pick a resource to target: maximize (opponent advantage over our current position).
    # If ties, prefer closer to us to reduce travel time.
    target = None
    best_key = None
    for rx, ry in resources:
        adv = cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)
        key = (adv, -cheb(sx, sy, rx, ry), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            target = (rx, ry)
    tx, ty = target

    # Evaluate all legal (or likely) moves by resulting advantage and distance progress.
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = [0, 0]
    best_score = None
    cur_d = cheb(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        new_d = cheb(nx, ny, tx, ty)
        adv = best_adv_for_target(tx, ty, nx, ny)
        progress = cur_d - new_d  # positive if closer
        # Small tie-break: keep moving in direction that reduces distance; then prefer lower coords.
        score = (adv, progress, -new_d, nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # Fallback: if all moves blocked, try staying.
    return best_move if best_score is not None else [0, 0]