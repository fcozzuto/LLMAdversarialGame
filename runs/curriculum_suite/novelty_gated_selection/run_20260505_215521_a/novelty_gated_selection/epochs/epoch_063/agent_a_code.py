def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Target selection with "steal priority": prefer resources where we're relatively closer than opponent.
    target = None
    if res:
        best = None
        for r in res:
            sd = cheb((sx, sy), r)
            od = cheb((ox, oy), r)
            adv = od - sd  # positive => we are closer
            # Prefer advantage, then our closeness, then deterministic tie-break.
            cand = (-(adv), sd, r[0], r[1])  # minimize
            if best is None or cand < best:
                best = cand
                target = r
        # If no meaningful advantage, fall back to nearest resource.
        if target is not None:
            sd = cheb((sx, sy), target)
            od = cheb((ox, oy), target)
            if od - sd <= 0:
                target = min(res, key=lambda t: (cheb((sx, sy), t), t[0], t[1]))

    if target is None:
        return [0, 0]

    tx, ty = target
    best_move = (0, 0)
    best_val = -10**18

    # Move scoring: advance toward target while avoiding giving opponent an immediate gain near the target.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        self_to_t = cheb((nx, ny), target)
        opp_to_t = cheb((ox, oy), target)
        # Encourage reducing self distance; slight tie to increase distance from opponent.
        val = -self_to_t + 0.1 * (opp_to_t - cheb((nx, ny), (ox, oy)))
        # If we would step adjacent to opponent, discourage (prevents being swept).
        if cheb((nx, ny), (ox, oy)) <= 1 and (nx, ny) != (ox, oy):
            val -= 0.6
        # Deterministic tie-break by move direction preference toward target.
        step_dir = (1 if tx > sx else (-1 if tx < sx else 0), 1 if ty > sy else (-1 if ty < sy else 0))
        val += 0.001 * (abs(dx - step_dir[0]) + abs(dy - step_dir[1]) == 0)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]