def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not inb(sx, sy) or (sx, sy) in blocked:
        sx, sy = 0, 0

    # If no resources, drift to opponent corner to reduce their options.
    if not resources:
        tx, ty = w - 1, h - 1
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            v = -md(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        # Choose move that maximizes our advantage over opponent for the single best obtainable resource.
        best_adv = -10**18
        best_own_dist = 10**9
        best_opp_dist = 10**9
        for rx, ry in resources:
            d_ours = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            adv = d_opp - d_ours  # positive means we are closer
            if adv > best_adv or (adv == best_adv and (d_ours < best_own_dist or (d_ours == best_own_dist and d_opp < best_opp_dist))):
                best_adv = adv
                best_own_dist = d_ours
                best_opp_dist = d_opp

        # Secondary objective: even when no positive advantage exists, help by blocking opponent pursuit
        # by moving to reduce their distance to the most contested resource.
        if best_adv >= 0:
            val = best_adv * 100 - best_own_dist
        else:
            # pick resource where opponent is closest, then reduce that distance.
            opp_best = 10**9
            for rx, ry in resources:
                d_opp = md(ox, oy, rx, ry)
                if d_opp < opp_best:
                    opp_best = d_opp
            # approximate improvement: how much we reduce our distance plus a small penalty for still being far
            # (keeps moves purposeful and deterministic).
            val = best_adv * 50 - best_own_dist - (opp_best)

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]