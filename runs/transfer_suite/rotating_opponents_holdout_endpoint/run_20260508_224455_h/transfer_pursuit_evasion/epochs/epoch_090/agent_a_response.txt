def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) and ("pursuer" not in role)

    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: fixed move order, evaluate all, pick best.
    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def corner_bonus(x, y):
        return (1 if x in (0, w - 1) else 0) + (1 if y in (0, h - 1) else 0)

    def blocked(nx, ny):
        return not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        d = dist2(nx, ny)
        cbonus = corner_bonus(nx, ny)

        # Safety vs pursuit
        # If evader: maximize distance, prefer corners.
        # If pursuer: minimize distance, also avoid dead ends near edges/obstacles.
        if is_evader:
            # Encourage moving away and toward corners; mild preference to approach opposite corner relative to pursuer.
            tx = 0 if ox > (w - 1) / 2 else (w - 1)
            ty = 0 if oy > (h - 1) / 2 else (h - 1)
            to_corner = (nx - tx) ** 2 + (ny - ty) ** 2
            # Higher key is better
            key = (d, cbonus, -to_corner)
        else:
            # Discourage positions too constrained: count available neighboring cells (including staying).
            free = 0
            for ddx, ddy in moves:
                ax, ay = nx + ddx, ny + ddy
                if not blocked(ax, ay):
                    free += 1
            key = (-d, -cbonus, -free)

        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]