def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            resources.append((rx, ry))
    if not resources:
        return [0, 0]

    # Heuristic: best target is one where opponent is relatively farther and we are closer.
    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx if dx >= 0 else -dx if False else None

    def abs_i(z):
        return z if z >= 0 else -z

    def cheb2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        adx = dx if dx >= 0 else -dx
        ady = dy if dy >= 0 else -dy
        return adx if adx >= ady else ady

    def man2(x1, y1, x2, y2):
        return abs_i(x1 - x2) + abs_i(y1 - y2)

    target = None
    best_key = None
    for rx, ry in resources:
        self_d = cheb2(sx, sy, rx, ry)
        opp_d = cheb2(ox, oy, rx, ry)
        # Prefer: large opp_d - self_d, then smaller self_d, then closer to our own side (smaller rx+ry).
        side = (rx + ry)
        key = ((opp_d - self_d) * 100 - self_d * 2 - side, -self_d, side, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            target = (rx, ry)

    tx, ty = target

    # Choose among all 9 deltas, avoiding obstacle cells, maximizing next-state desirability.
    deltas = (-1, 0, 1)
    best_move = [0, 0]
    best_val = None

    def valid_cell(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    for dx in deltas:
        for dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid_cell(nx, ny):
                continue
            # If move reaches a resource, heavily prefer.
            on_res = 1 if (nx, ny) in set(resources) else 0
            self_d = cheb2(nx, ny, tx, ty)
            # Opponent pressure: how much closer/farther we are relative to opponent from next position.
            opp_d = cheb2(ox, oy, tx, ty)
            # Bonus for reducing distance to target; slight penalty for staying still.
            val = (on_res * 10_000
                   + (opp_d - self_d) * 200
                   - self_d * 5
                   - (1 if (dx == 0 and dy == 0) else 0) * 2
                   + (-man2(nx, ny, ox, oy)) * 0.5)
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move