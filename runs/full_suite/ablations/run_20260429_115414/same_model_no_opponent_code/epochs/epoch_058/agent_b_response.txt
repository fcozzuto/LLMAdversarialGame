def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        res = [(w // 2, h // 2)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick target deterministically: nearest (manhattan), tie by x then y
    tx, ty = res[0]
    best = man(sx, sy, tx, ty)
    for rx, ry in res[1:]:
        d = man(sx, sy, rx, ry)
        if d < best or (d == best and (rx < tx or (rx == tx and ry < ty))):
            best, tx, ty = d, rx, ry

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_cost = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        d_target = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)

        # Encourage collecting if stepping onto a resource.
        on_res = 1 if (nx, ny) in res else 0

        cost = d_target
        cost -= 120 * on_res
        cost -= 1.5 * d_opp  # prefer moving away from opponent

        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_move = (dx, dy)
        elif cost == best_cost:
            # deterministic tie-breaker: earlier in moves list
            # (current best_move already corresponds to earlier move due to update rule)
            pass

    return [int(best_move[0]), int(best_move[1])]