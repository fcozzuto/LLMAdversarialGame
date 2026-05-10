def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target resources we can reach first, and also that keep opponent farther.
    best = None
    best_key = None
    for rx, ry in resources:
        s_d = cheb((sx, sy), (rx, ry))
        o_d = cheb((ox, oy), (rx, ry))
        # Lower is better: prioritize smaller self distance and larger opponent distance.
        key = (s_d - 1.25 * o_d, s_d, o_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # Candidate step deltas in deterministic preference order.
    deltas = []
    dx = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    dy = 0
    if ty > sy: dy = 1
    elif ty < sy: dy = -1
    deltas.append((dx, dy))
    if dx != 0 or dy != 0:
        deltas.append((dx, 0))
        deltas.append((0, dy))
        deltas.append((dx, -dy))
        deltas.append((-dx, dy))
    deltas.append((0, 0))
    # Fill with other adjacent options for robustness.
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            if (a, b) != (0, 0) and (a, b) not in deltas:
                deltas.append((a, b))

    # Choose among valid moves the one that improves our advantage against the opponent.
    best_move = (0, 0)
    best_move_key = None
    for mdx, mdy in deltas:
        nx, ny = sx + mdx, sy + mdy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Advance toward target and avoid giving opponent an easy next access.
        ns = cheb((nx, ny), (tx, ty))
        no = cheb((ox, oy), (tx, ty))
        # Also slightly punish moving closer to opponent generally.
        opp_general = cheb((nx, ny), (ox, oy))
        key = (ns - 0.35 * no, opp_general, abs(nx - sx) + abs(ny - sy), nx, ny, mdx, mdy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]