def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def clamp(nx, ny):
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            return sx, sy
        return nx, ny

    def md(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    if not res:
        # Chase nearest corner-ish resource-less fallback: move away from opponent if adjacent, else toward farther corner
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = clamp(sx + dx, sy + dy)
            d1 = md(nx, ny, ox, oy)
            bonus = d1 if (abs(nx-ox) <= 1 and abs(ny-oy) <= 1) else -d1
            if bonus > best[2]:
                best = (dx, dy, bonus)
        return [best[0], best[1]]

    # Evaluate each move by best "advantage" resource after that move.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = clamp(sx + dx, sy + dy)
        best_adv = -10**18
        best_sd = 10**9
        for rx, ry in res:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd  # higher means we get there first (or deny)
            if adv > best_adv or (adv == best_adv and (sd < best_sd or (sd == best_sd and (rx+ry) < (0)))):
                best_adv = adv
                best_sd = sd
        # Prefer minimizing our distance when advantages tie; slight preference to moving closer to any resource.
        any_near = min(md(nx, ny, rx, ry) for rx, ry in res)
        val = best_adv * 1000 - best_sd * 10 - any_near
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]