def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if (sx, sy) in resources:
        return [0, 0]

    opp = (ox, oy)
    my = (sx, sy)
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    tr = int(observation.get("turns_remaining", 0) or 0)

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        dm0 = 0  # placeholder, computed below
        ns = (nx, ny)

        best_adv = None
        best_dm = None
        for t in resources:
            dm = man(ns, t)
            do = man(opp, t)
            adv = do - dm  # positive means we are closer than opponent
            # Encourage reachable resources; discourage "give-away" where opponent is far ahead
            if tr > 0:
                if dm > tr:
                    adv -= 1000
                if do > tr and adv > 0:
                    adv += 1
            key_adv = adv
            if best_adv is None or key_adv > best_adv or (key_adv == best_adv and (best_dm is None or dm < best_dm)):
                best_adv = key_adv
                best_dm = dm

        # Prefer moves that secure more advantage; tie-break by smaller distance to the best target
        val = (best_adv, -best_dm if best_dm is not None else 0, -abs(nx - (w - 1)), -abs(ny - (h - 1)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]