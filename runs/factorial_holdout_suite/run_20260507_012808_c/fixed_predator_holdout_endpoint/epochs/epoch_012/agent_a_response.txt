def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        cx, cy = w // 2, h // 2
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            self_d = abs(nx - cx) + abs(ny - cy)
            opp_d = abs(nx - ox) + abs(ny - oy)
            sc = (opp_d - self_d)
            if sc > best[1]:
                best = ((dx, dy), sc)
        return [best[0][0], best[0][1]] if best[0] else [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best_adv = -10**9
        best_self_d = 10**9
        best_r = None
        for rx, ry in resources:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            adv = opp_d - self_d
            if adv > best_adv or (adv == best_adv and self_d < best_self_d):
                best_adv = adv
                best_self_d = self_d
                best_r = (rx, ry)
        # Prefer securing an earlier resource; tie-break by being closer to it and moving toward it.
        target = best_r
        direct = md(nx, ny, target[0], target[1]) if target else 0
        cur_to_target = md(sx, sy, target[0], target[1]) if target else 0
        improved = cur_to_target - direct
        sc = best_adv * 1000 - best_self_d * 3 + improved
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]