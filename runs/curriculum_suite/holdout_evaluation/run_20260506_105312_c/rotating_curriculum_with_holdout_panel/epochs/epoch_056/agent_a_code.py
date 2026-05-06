def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def md(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = md(nx, ny, tx, ty)
            key = (d, abs(nx - tx) + abs(ny - ty), dx, dy)
            if best is None or key < best:
                best = key
        return [best[2], best[3]] if best else [0, 0]

    # Deny: target resources where opponent is relatively closer than we are.
    target = None
    best_key = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Prefer: (opponent_closer) -> od - sd minimal; tie-breaker: actually close overall
        key = (od - sd, sd + od, abs(rx - ox) + abs(ry - oy), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            target = (rx, ry)

    rx, ry = target
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # After move, re-check denial objective for robustness
        sd = md(nx, ny, rx, ry)
        od = md(ox, oy, rx, ry)
        key = (od - sd, sd, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best is None or key < best:
            best = key
    return [best[3], best[4]] if best else [0, 0]