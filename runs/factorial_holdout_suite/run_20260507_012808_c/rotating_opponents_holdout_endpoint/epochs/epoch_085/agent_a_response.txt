def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer resources where we are not worse in (Manhattan) arrival.
    # If we are tied, prefer the one farther from opponent's position.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds  # positive => we arrive earlier
        edge = (1 if rx == 0 or rx == w - 1 else 0) + (1 if ry == 0 or ry == h - 1 else 0)
        # small bias to avoid corners unless clearly winning there
        key = (adv, -ds, -edge, -man(rx, ry, w - 1 - ox, h - 1 - oy), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_move_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ds2 = man(nx, ny, rx, ry)
        # Re-evaluate advantage at the next step for the chosen target
        do2 = man(ox, oy, rx, ry)
        adv2 = do2 - ds2

        # Additional micro-avoidance: prefer moves that don't get stuck near an obstacle wall.
        neigh_block = 0
        for tx, ty in dirs:
            ax, ay = nx + tx, ny + ty
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                neigh_block += 1

        # Also allow opportunistic switch: if a different resource becomes clearly better, pick that move.
        # Keep this cheap: only check best few by direct advantage at next step.
        opportun = -10**9
        for (rrx, rry) in resources:
            dss = man(nx, ny, rrx, rry)
            doo = man(ox, oy, rrx, rry)
            val = doo - dss
            if val > opportun:
                opportun = val
            if opportun >= adv2 + 2:
                break

        key = (opportun, adv2, -ds2, -neigh_block, -abs((rx - nx)) - abs((ry - ny)))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]