def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Choose a contested target: maximize how much closer we are than opponent.
    best_r = None
    best_adv = None
    any_res = False
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) == 2):
            continue
        rx, ry = r[0], r[1]
        if not (isinstance(rx, int) and isinstance(ry, int) and 0 <= rx < w and 0 <= ry < h):
            continue
        if (rx, ry) in obs:
            continue
        any_res = True
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        adv = do - ds
        if best_adv is None or adv > best_adv or (adv == best_adv and ds < md(sx, sy, best_r[0], best_r[1])):
            best_adv = adv
            best_r = (rx, ry)

    # Fallback: if no resource found, move toward center.
    if not any_res:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        target = (tx, ty)
        best_r = None
    else:
        target = best_r

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            if best_r is None:
                dnew = abs(nx - target[0]) + abs(ny - target[1])
                # deterministic tie-break prefers moving diagonally when equally good
                score = -dnew + (1 if dx != 0 and dy != 0 else 0) * 1e-6
            else:
                rx, ry = target
                dself = md(nx, ny, rx, ry)
                ds_cur = md(sx, sy, rx, ry)
                do = md(ox, oy, rx, ry)
                # prefer reducing our distance and also resources where we keep an edge
                score = (do - dself) * 10.0 - dself - 0.5 * (dself == ds_cur)
                # slight bias to approach blocked regions' frontier: prefer moves that aren't walls-nearby
                # count free neighbors
                free_nb = 0
                for ddx in (-1, 0, 1):
                    for ddy in (-1, 0, 1):
                        if ddx == 0 and ddy == 0:
                            continue
                        xx, yy = nx + ddx, ny + ddy
                        if valid(xx, yy):
                            free_nb += 1
                score += free_nb * 0.05
                if dx != 0 and dy != 0:
                    score += 0.001
            cand.append((score, dx, dy))

    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (t[0], -t[1] * 0 - t[2] * 0, 0), reverse=True)
    _, dx, dy = cand[0]
    return [int(dx), int(dy)]