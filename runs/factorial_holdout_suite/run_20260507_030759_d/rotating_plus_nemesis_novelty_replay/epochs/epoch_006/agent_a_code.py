def choose_move(observation):
    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
            p = v.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return int(p[0]), int(p[1])
        return 0, 0

    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = xy(observation.get("self_position"))
    ox, oy = xy(observation.get("opponent_position"))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        x, y = xy(o)
        obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Intercept strategy: take resources we can reach strictly earlier than the opponent.
        local_best = -10**18
        for r in resources:
            rx, ry = xy(r)
            myd = abs(rx - nx) + abs(ry - ny)
            opd = abs(rx - ox) + abs(ry - oy)
            # Prefer winning captures; then prefer earlier captures; then slightly prefer farther from opponent.
            sc = (opd - myd) * 1000 - myd * 2 + (opd - myd >= 1) * 100
            if (opd - myd >= 1) and myd == 0:
                sc += 10**6
            if sc > local_best:
                local_best = sc
        # Tie-break deterministically: prefer moves that reduce distance to opponent-targeted area by nudging toward own best.
        if local_best > best_sc:
            best_sc = local_best
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [int(dx), int(dy)]