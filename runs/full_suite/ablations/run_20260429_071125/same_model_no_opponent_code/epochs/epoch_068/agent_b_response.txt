def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Prefer grabbing the closest resource, but only if we are competitive vs opponent.
        my_best = 10**9
        opp_best = 10**9
        attack = 0
        for rx, ry in resources:
            d_my = dist(nx, ny, rx, ry)
            d_op = dist(ox, oy, rx, ry)
            if d_my < my_best: my_best = d_my
            if d_op < opp_best: opp_best = d_op
            # If we can reach it sooner or tie, it gets bonus. If we are far behind, penalize.
            diff = d_op - d_my
            if diff >= 0:
                attack += 1200 - 40 * d_my
            else:
                attack -= 25 * (-diff) + 8 * d_my

        # Secondary: keep improving shortest path to any resource; also slight repulsion from opponent.
        opp_rep = dist(nx, ny, ox, oy)
        val = 2_000_000 - 2000 * my_best + attack + 3 * opp_rep - 20 * opp_best
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]