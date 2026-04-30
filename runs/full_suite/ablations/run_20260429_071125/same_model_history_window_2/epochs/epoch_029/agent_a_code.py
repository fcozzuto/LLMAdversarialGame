def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = man(nx, ny, ox, oy)  # drift away if no resources
            if val > best[2]:
                best = (dx, dy, val)
        return [best[0], best[1]] if best[2] > -10**8 else [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Choose the resource that maximizes advantage (opp_dist - self_dist)
        best_adv = -10**18
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - self_d
            if adv > best_adv:
                best_adv = adv
        # Small tie-breakers: prefer closer to opponent (reduce threat) and closer overall to resources
        opp_closer = -man(nx, ny, ox, oy) * 0.01
        self_closest = min(man(nx, ny, rx, ry) for rx, ry in resources) * 0.001
        val = best_adv + opp_closer - self_closest
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]