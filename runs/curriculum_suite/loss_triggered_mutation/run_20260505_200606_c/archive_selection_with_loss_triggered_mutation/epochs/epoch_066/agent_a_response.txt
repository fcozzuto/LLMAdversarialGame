def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        # Deterministic fallback: move to increase distance from opponent while progressing toward board center.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = (man(nx, ny, ox, oy) * 3) - (man(nx, ny, cx, cy) * 1)
            if best is None or v > bestv or (v == bestv and (nx, ny) < best):
                best = (nx, ny)
                bestv = v
        if best is None:
            return [0, 0]
        return [best[0] - sx, best[1] - sy]

    dcur_so = man(sx, sy, ox, oy)

    # Choose the resource where we have the strongest "tempo" advantage.
    best_res = None
    best_adv = None
    for rx, ry in resources:
        adv = man(ox, oy, rx, ry) - man(sx, sy, rx, ry)
        # Prefer resources that are not behind obstacles-free distance (softly)
        if best_res is None or adv > best_adv or (adv == best_adv and (rx, ry) < best_res):
            best_adv = adv
            best_res = (rx, ry)

    tx, ty = best_res

    # If opponent is extremely close, prioritize escape while still moving toward the best_res.
    escape_mode = (dcur_so <= 2)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        dself = man(nx, ny, tx, ty)
        dopp = man(nx, ny, ox, oy)
        dopp_to_res = man(ox, oy, tx, ty)
        self_to_res_cur = man(sx, sy, tx, ty)
        opp_to_res_cur = dopp_to_res

        # Primary: reduce our distance to chosen resource.
        # Secondary: keep/establish tempo advantage (we want opponent's distance to be larger than ours).
        # Tertiary: avoid moving into opponent pressure.
        tempo_after = opp_to_res_cur - dself

        if escape_mode:
            val = (dopp * 4) + (tempo_after * 1) - (dself * 1.5)
        else:
            val = (tempo_after * 3.0) + (dopp * 0.8) - (dself * 2.2)

        # Slight deterministic tie-break: prefer staying still only if equal.
        val -= 0.01 * (0 if (dx, dy) == (0, 0) else 1)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]