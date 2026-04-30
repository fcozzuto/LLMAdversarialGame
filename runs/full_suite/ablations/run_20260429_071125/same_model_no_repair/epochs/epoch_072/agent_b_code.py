def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obst = set((int(p[0]), int(p[1])) for p in obstacles if p is not None and len(p) >= 2)
    resources = observation.get("resources") or []
    res = [tuple(map(int, p)) for p in resources if p and len(p) >= 2 and (int(p[0]), int(p[1])) not in obst]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move, best_val = (0, 0), -10**18
    target_corner = (0, 0) if (ox + oy) > (w - 1 - sx + h - 1 - sy) else (w - 1, h - 1)
    have_resources = len(res) > 0

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        if have_resources:
            # Choose move that most increases "lead" at some resource, with slight tie-break toward nearer resources.
            cur_best = -10**18
            for rx, ry in res:
                md = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # Prefer resources I can reach no worse than opponent; encourage closeness to reduce future contest.
                v = (od - md) * 10 - md
                # Mildly avoid moving away from my current direction by encouraging progress toward chosen resource.
                v += 0.2 * (cheb(sx, sy, rx, ry) - cheb(nx, ny, rx, ry))
                if v > cur_best:
                    cur_best = v
            val = cur_best
        else:
            # No visible resources: head toward the safer opposite-ish corner from opponent, favor moving closer.
            tx, ty = target_corner
            val = -cheb(nx, ny, tx, ty) - 0.3 * cheb(nx, ny, ox, oy)
        # Deterministic tie-break: prefer smaller |dx|+|dy| then deterministic ordering.
        dist_still = abs(dx) + abs(dy)
        val2 = (val, -dist_still, dx, dy)
        if val2 > (best_val, - (abs(best_move[0]) + abs(best_move[1])), best_move[0], best_move[1]):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]