def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]
    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    best = (0, 0)
    best_val = -10**18
    # Prefer moves that secure a resource where we are significantly closer than opponent.
    # If we can't secure, still minimize our distance to the best remaining resource.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        local_best = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if sd == 0:
                val = 10**9 - od  # immediate collection
            else:
                # Materially favor "reach first" opportunities; tie-break toward closer overall.
                val = (od - sd) * 1000 - sd * 3
            if val > local_best:
                local_best = val

        # Tie-break deterministically: higher local_best, then smaller move cost, then lexicographic preference.
        move_cost = abs(dx) + abs(dy)
        val = local_best - move_cost * 0.1
        if val > best_val or (val == best_val and (move_cost, dx, dy) < (abs(best[0]) + abs(best[1]), best[0], best[1])):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]