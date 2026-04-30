def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a target where we have relative advantage over opponent.
    best_t = None
    best_adv = -10**18
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        adv = (op_d - my_d) * 10 - my_d
        if adv > best_adv:
            best_adv = adv
            best_t = (rx, ry)

    tx, ty = best_t

    # Score each move: improve our distance to target, worsen opponent distance, and avoid bad contact.
    best_m = (0, 0)
    best_v = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(ox, oy, tx, ty)

        # If we step onto any resource, prioritize strongly.
        step_res = 1 if (nx, ny) in set(resources) else 0

        # Push away from opponent slightly unless we can grab immediately.
        opp_d = cheb(nx, ny, ox, oy)

        # Avoid moves that reduce relative advantage for the target.
        cur_my_d = cheb(sx, sy, tx, ty)
        rel_now = op_d - cur_my_d
        rel_after = op_d - my_d

        v = 0
        v += (10000 if step_res else 0)
        v += -my_d * 20
        v += -(max(0, rel_now - rel_after)) * 35  # discourage losing target advantage
        v += opp_d * (2 if not step_res else 0)
        v += (8 if op_d > cur_my_d else -4)  # pressure if we're ahead

        # Tie-break deterministically by dir order through strict > comparison; keep first.
        if v > best_v:
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]