def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [int(dx), int(dy)]
        return [0, 0]

    if resources:
        best_t = None
        best_adv = None  # smaller is better: our_dist - opp_dist
        for tx, ty in resources:
            adv = abs(sx - tx) + abs(sy - ty) - (abs(ox - tx) + abs(oy - ty))
            # tie-break: closer to us
            d = abs(sx - tx) + abs(sy - ty)
            if best_adv is None or adv < best_adv or (adv == best_adv and d < (abs(sx - best_t[0]) + abs(sy - best_t[1]))):
                best_adv = adv
                best_t = (tx, ty)

        tx, ty = best_t
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            our_d = abs(nx - tx) + abs(ny - ty)
            opp_d = abs(ox - tx) + abs(oy - ty)
            # prefer reducing our distance; also prefer moves that don't let opponent get closer advantage
            val = -our_d - 0.2 * (our_d - opp_d)
            # slight anti-crowd: avoid stepping closer to opponent unless it also reduces our target distance
            val -= 0.05 * (abs(nx - ox) + abs(ny - oy))
            # prefer landing on resource
            if (nx, ny) == (tx, ty):
                val += 1000
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        # No visible resources: drift to maximize distance from opponent while staying central-ish
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = (abs(nx - ox) + abs(ny - oy)) - 0.1 * (abs(nx - cx) + abs(ny - cy))
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]