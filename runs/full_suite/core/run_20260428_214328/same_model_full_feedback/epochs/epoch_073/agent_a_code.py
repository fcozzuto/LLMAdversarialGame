def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = md((nx, ny), (ox, oy))
            if d > best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        self_pos = (nx, ny)
        opp_pos = (ox, oy)

        # Choose the resource where we'd be closest relative to the opponent (current positions as proxy).
        best_adv = -10**18
        best_sd = 10**18
        for r in resources:
            sd = md(self_pos, r)
            od = md(opp_pos, r)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and sd < best_sd):
                best_adv = adv
                best_sd = sd

        # Prefer larger relative advantage; break ties by closer self distance; small penalty to avoid drifting.
        opp_to_best = best_sd + best_adv
        val = best_adv * 1000 - best_sd - (0 if dx == 0 and dy == 0 else 0.01 * (abs(dx) + abs(dy))) - 0.001 * opp_to_best
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]