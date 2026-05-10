def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obs.add((px, py))

    valid_res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                valid_res.append((rx, ry))

    if not valid_res:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in valid_res:
        sd = cheb((sx, sy), (rx, ry))
        od = cheb((ox, oy), (rx, ry))
        # Prefer stronger contest (opp farther), then nearer for us, then lower coordinates for determinism
        key = ((od - sd) * 1000 + (-sd) * 10 + (ry * -1) + (rx * -1), -sd, -od, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_m_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        nd = cheb((nx, ny), (tx, ty))
        # Keep contest pressure: how much nearer we are than opponent after this move
        my_adv = cheb((ox, oy), (tx, ty)) - nd
        # Prefer reducing distance, and bias toward target
        key = (my_adv * 1000 + (-nd) * 10 + (-abs(tx - nx)) + (-abs(ty - ny)), -nd, -nx, -ny)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]