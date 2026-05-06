def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Preselect a small set of promising targets based on who is closer
    best_targets = []
    for tx, ty in res:
        myd = md(sx, sy, tx, ty)
        opd = md(ox, oy, tx, ty)
        # Prefer resources where opponent is not significantly closer, but where we can gain tempo
        gain = (opd - myd)
        if myd == 0:
            gain += 5
        # discourage very far targets from both
        gain -= 0.15 * (myd + opd)
        best_targets.append((gain, tx, ty, myd, opd))
    best_targets.sort(key=lambda t: (-(t[0]), t[3], t[4], t[1], t[2]))
    targets = [(t[1], t[2], t[3], t[4]) for t in best_targets[:5]]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break order already fixed by list ordering
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        # Local evaluation: maximize advantage over the best target after this move
        val = -10**18
        for tx, ty, myd0, opd0 in targets:
            myd1 = md(nx, ny, tx, ty)
            opd = opd0  # opponent position unchanged
            # Strongly reward becoming the closer collector; penalize giving opponent tempo
            step_adv = (opd - myd1) - 0.2 * myd1
            if myd1 == 0:
                step_adv += 10
            # Mild tie-break for reducing opponent's next advantage on that target
            step_adv -= 0.05 * max(0, myd1 - opd)
            if step_adv > val:
                val = step_adv
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]