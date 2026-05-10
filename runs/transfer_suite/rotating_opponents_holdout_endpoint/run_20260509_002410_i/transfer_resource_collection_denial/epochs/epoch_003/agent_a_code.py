def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Targeting: prefer cells where we get there earlier than opponent; break ties toward denying opponent by proximity to them.
    best = None
    bestt = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds
        # Anticipate sweep_rows: if opponent is far in y, favor staying closer in y (reduces their sweep utility)
        y_bias = -(abs(ry - oy) - abs(ry - sy))
        key = (lead, y_bias, -ds, -cheb(ox, oy, rx, ry), rx, ry)
        if best is None or key > best:
            best = key
            bestt = (rx, ry)

    if bestt is None:
        return [0, 0]
    tx, ty = bestt

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Obstacle avoidance + deterministic scoring
    cur_ds = cheb(sx, sy, tx, ty)
    cur_do = cheb(ox, oy, tx, ty)
    bestm = None
    bestk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        nds = cheb(nx, ny, tx, ty)
        # Opponent assumed greedy toward same target; still account via relative progress
        nlead = cur_do - nds
        step_gain = cur_ds - nds  # positive if we get closer
        # If tie, prefer moves that reduce both x and y discrepancy to help diagonal reachability
        nxyd = abs(tx - nx) + abs(ty - ny)
        # Also keep from "oscillating": small preference to move in the direction of target
        dir_pref = -((0 if dx == 0 else (1 if tx > sx else -1) != dx) or (0))
        key = (nlead, step_gain, -nxyd, dx, dy)
        if bestk is None or key > bestk:
            bestk = key
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]