def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def cd(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def score_res(rx, ry):
        ds = cd(sx, sy, rx, ry)
        do = cd(ox, oy, rx, ry)
        # Prefer resources we can reach at least as fast; then closer; then bottom-right bias
        return (0 if ds <= do else 1, ds, -rx - ry)

    if resources:
        best = None
        bestk = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                if (rx, ry) not in obs and inb(rx, ry):
                    k = score_res(rx, ry)
                    if best is None or k < bestk:
                        best = (rx, ry)
                        bestk = k
        if best is None:
            best = (min([r[0] for r in resources]), min([r[1] for r in resources])) if resources else (sx, sy)
        tx, ty = best
    else:
        # No visible resources: drift to the side less likely controlled by opponent
        if ox < w // 2:
            tx = w - 1
        else:
            tx = 0
        if oy < h // 2:
            ty = h - 1
        else:
            ty = 0

    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # primary: reduce distance to target
        d = cd(nx, ny, tx, ty)
        # secondary: avoid giving opponent a tighter line (denier archetype)
        opp_d = cd(ox, oy, nx, ny)
        val = (d, opp_d)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]