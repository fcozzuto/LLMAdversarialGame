def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not inb(sx, sy):
        return [0, 0]

    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if inb(rx, ry) and (rx, ry) not in obstacles:
                res_list.append((rx, ry))
    res_set = set(res_list)

    # Choose a target deterministically: nearest to self, tie by nearer to opponent, then by coordinates.
    tx, ty = ox, oy
    if res_list:
        best = None
        for rx, ry in res_list:
            key = (man(sx, sy, rx, ry), man(ox, oy, rx, ry), rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue
        # Prefer collecting, then approaching target; also avoid moving into opponent vicinity.
        val = 0.0
        if (nx, ny) in res_set:
            val += 1000.0
        d_t = man(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        val += -2.2 * d_t
        # Strongly prefer being farther from opponent, but allow diagonal chasing if beneficial.
        val += 8.0 * d_o
        # Lightly encourage advancing relative to opponent towards the target.
        val += 0.6 * (man(ox, oy, tx, ty) - man(nx, ny, tx, ty))
        # Small tie-breaker: prefer moves that reduce chebyshev distance to opponent when target empty (harass).
        if not res_list:
            val += -0.2 * cheb(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]