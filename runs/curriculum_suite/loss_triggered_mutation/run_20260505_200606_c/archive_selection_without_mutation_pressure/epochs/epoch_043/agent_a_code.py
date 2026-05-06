def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    on_edge = (ox == 0 or ox == w - 1 or oy == 0 or oy == h - 1)
    best = None
    best_key = None
    parity = observation.get("turn_index", 0) & 1

    if on_edge:
        # Race the opponent on their edge by targeting the closest remaining resource to them.
        for rx, ry in resources:
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer slightly nearer-to-us among ties; deterministic tie-break by coords.
            key = (d_opp, cheb(sx, sy, rx, ry), (rx + ry) % 2, rx, ry)
            if best is None or key < best_key:
                best_key = key
                best = (rx, ry)
    else:
        # Otherwise, use advantage targeting: resources where we are closer than the opponent.
        for rx, ry in resources:
            d_self = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_self
            # Tie-break: prefer resources that are not too "odd-parity" away from us.
            key = (-adv, d_self, (rx + ry) % 2 if parity == 0 else 1 - (rx + ry) % 2, rx, ry)
            if best is None or key < best_key:
                best_key = key
                best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_next = cheb(nx, ny, tx, ty)
        d_opp_next = cheb(ox, oy, tx, ty)
        # Primary: minimize distance to target; Secondary: maximize "race" margin; Tertiary: deterministic tie-break.
        key = (d_next, -(d_opp_next - d_next), (abs(nx - w // 2) + abs(ny - h // 2)) % 2, dx, dy)
        if best_score is None or key < best_score:
            best_score = key
            best_move = [dx, dy]

    return best_move if best_score is not None else [0, 0]