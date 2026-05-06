def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    edge_dist = min(sx, sy, w - 1 - sx, h - 1 - sy)
    op_edge_dist = min(ox, oy, w - 1 - ox, h - 1 - oy)

    def edge_nearness(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    def edge_risk(x, y):
        # If opponent is already close to an edge, avoid moving to edges (edge_patrol counter).
        if op_edge_dist <= 2:
            return -2.0 if edge_nearness(x, y) == 0 else (-1.0 if edge_nearness(x, y) == 1 else 0.0)
        return -1.0 if edge_nearness(x, y) == 0 and edge_dist <= 1 else 0.0

    # Choose a target resource with a different tie-break than the incumbent:
    # Prefer (1) resources where we can improve advantage soon, (2) interior control,
    # and (3) avoid giving the opponent an even tighter chase.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # positive => we are closer
        center = -(abs(rx - cx) + abs(ry - cy))
        # If opponent is closer, only take it if we can still cut them down.
        cut = (od - (sd - 1)) if od > sd else (adv + 1)
        # Encourage interior without ignoring advantage.
        key = (adv, cut, center, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Race progress plus edge-risk penalty; deterministic tie-break on coordinates.
        val = (opd - myd, -myd, -(abs(nx - rx) + abs(ny - ry)), edge_risk(nx, ny), -nx, -ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]