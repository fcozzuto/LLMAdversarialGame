def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(int(p[0]), int(p[1])) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def d(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    adj4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    adj8 = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def obst_pen(x, y):
        if (x, y) in occ:
            return 10**9
        p = 0
        for dx, dy in adj4:
            if (x + dx, y + dy) in occ:
                p += 6
        for dx, dy in adj8:
            if (x + dx, y + dy) in occ:
                p += 2
        return p

    cx, cy = (w - 1) // 2, (h - 1) // 2

    if resources:
        best_r = None
        best_val = -10**18
        for rx, ry in resources:
            sd = d(sx, sy, rx, ry)
            od = d(ox, oy, rx, ry)
            # Prefer resources we are closer to; also prefer closer overall.
            val = (od - sd) * 2 - sd * 0.25
            # Tiny deterministic tie-break
            val += (rx * 17 + ry * 31) * 1e-6
            if val > best_val:
                best_val, best_r = val, (rx, ry)
        tx, ty = best_r
        target_dist = d(sx, sy, tx, ty)

        best_move = (0, 0)
        best_score = -10**18
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            self_to_t = d(nx, ny, tx, ty)
            opp_to_t = d(ox, oy, tx, ty)
            # Keep attacking the contested target; if we get worse vs opponent, avoid it.
            adv = opp_to_t - self_to_t
            # Also consider reaching any resource nearby (prevents dead-ends).
            near_best = 0
            for rx, ry in resources:
                nd = d(nx, ny, rx, ry)
                near_best = max(near_best, (d(ox, oy, rx, ry) - nd) * 0.4 - nd * 0.08)
            opp_dist = d(nx, ny, ox, oy)
            score = adv * 3 - self_to_t * 0.6 + near_best + (opp_dist * 0.05) - obst_pen(nx, ny) * 1.0
            # Prefer reducing distance to target immediately
            score += (target_dist - self_to_t) * 0.35
            if score > best_score:
                best_score = score
                best_move = (dxm, dym)
        return [int(best_move[0]), int(best_move[1])]
    else:
        best_move = (0, 0)
        best_score = -10**18
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym