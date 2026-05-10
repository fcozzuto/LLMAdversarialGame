def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    pursuer = ("pursu" in role) or ("chase" in role) or ("capt" in role)
    evader = ("evad" in role) or ("escap" in role)
    if not pursuer and evader:
        pursuer = False
    if not pursuer and not evader and not pursuer:
        pursuer = True

    obs_set = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x", -1)), int(p.get("y", -1))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def local_obst_pen(x, y):
        if (x, y) in obs_set:
            return 10_000_000
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obs_set:
                    pen += 5
        return pen

    # Heuristic: evaluate candidate next positions; deterministic tie-break by move order.
    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            sc = -10_000_000 if pursuer else -10_000_000
        else:
            d = dist2(nx, ny)
            # Bias: keep progress toward/away while avoiding obstacles.
            if pursuer:
                sc = (-d * 10) - local_obst_pen(nx, ny)
                # Prefer moves that reduce Manhattan when tied with diagonal clutter.
                man_before = abs(sx - ox) + abs(sy - oy)
                man_after = abs(nx - ox) + abs(ny - oy)
                sc += (man_before - man_after) * 3
            else:
                sc = (d * 10) - local_obst_pen(nx, ny)
                man_before = abs(sx - ox) + abs(sy - oy)
                man_after = abs(nx - ox) + abs(ny - oy)
                sc += (man_after - man_before) * 3
                # Extra: avoid drifting directly into the opponent's neighborhood if too close.
                if d <= 4:
                    sc -= 30
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]