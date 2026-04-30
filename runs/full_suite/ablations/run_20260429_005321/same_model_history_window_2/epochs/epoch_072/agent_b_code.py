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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Pick resources where we can potentially beat opponent (opponent not strictly closer).
    best_target = None
    best_pair = (-10**9, -10**9)
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer targets we are closer to; otherwise weaker preference for "not losing too hard".
        pair = (do - ds, -ds)
        if pair > best_pair:
            best_pair = pair
            best_target = (rx, ry)

    # If no resources exist, just keep distance from opponent while respecting obstacles.
    if best_target is None:
        best_move = [0, 0]
        best_val = -10**9
        for dx, dy, nx, ny in candidates:
            val = cheb(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
        return best_move

    tx, ty = best_target
    best_move = [0, 0]
    best_val = -10**18

    # Evaluate each candidate by how much it improves relative advantage to the chosen target,
    # plus a mild repulsion from opponent to avoid getting intercepted.
    for dx, dy, nx, ny in candidates:
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        rel = (do - ds)  # higher is better
        adv = rel * 4 - ds
        rep = cheb(nx, ny, ox, oy)
        # If we are adjacent to opponent, emphasize repulsion deterministically.
        if cheb(nx, ny, ox, oy) <= 1:
            adv += rep * 6
        else:
            adv += rep * 1
        if adv > best_val:
            best_val = adv
            best_move = [dx, dy]

    return best_move