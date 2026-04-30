def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = [(int(x), int(y)) for x, y in (observation.get("resources") or [])]
    obstacles = {(int(x), int(y)) for x, y in (observation.get("obstacles") or [])}

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def near_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    def best_value(nx, ny):
        if not resources:
            return 0.0
        best = -10**18
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            gap = opp_d - our_d
            take = 10.0 if our_d == 0 else 0.0
            # Prefer resources we can reach not much later than opponent, and generally closer.
            v = 2.2 * gap - 0.4 * our_d + take
            # Mild bias toward earlier opponent-distance advantage (contested targets)
            v += 0.15 * (opp_d - our_d == 1)
            if v > best: best = v
        return best

    bestm = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        v = best_value(nx, ny)
        # Obstacle/edge safety and keep deterministic tie-breaking
        v -= 0.15 * near_obs(nx, ny)
        # If no strong target signal yet, move to reduce distance to the nearest resource
        if resources:
            nearest = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            v -= 0.05 * nearest
        # Deterministic tie-break: prefer smaller |dx|+|dy|, then lexicographic
        key = (v, - (abs(dx) + abs(dy)), -dx, -dy)
        if key > (bestv, - (abs(bestm[0]) + abs(bestm[1])), -bestm[0], -bestm[1]):
            bestv = v
            bestm = [dx, dy]
    return [int(bestm[0]), int(bestm[1])]