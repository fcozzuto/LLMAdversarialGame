def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b, x, y):
        dx = a - x
        if dx < 0: dx = -dx
        dy = b - y
        if dy < 0: dy = -dy
        return dx + dy

    # If we're already on a resource, stay or step off deterministically: staying is fine.
    if (sx, sy) in set(resources):
        return [0, 0]

    # Choose next move that maximizes "we get there first" against opponent.
    best = None
    best_move = (0, 0)
    res_set = set(resources)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        # Reward immediate collection, then maximize advantage on best target.
        collect = 1 if (nx, ny) in res_set else 0
        # Evaluate best resource from this candidate position.
        local_best_adv = -10**9
        local_best_self = 10**9
        for rx, ry in resources:
            self_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            adv = opp_d - self_d
            if adv > local_best_adv or (adv == local_best_adv and self_d < local_best_self):
                local_best_adv = adv
                local_best_self = self_d
        val = (collect, local_best_adv, -local_best_self, -abs(nx - sx) - abs(ny - sy))
        if best is None or val > best:
            best = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]