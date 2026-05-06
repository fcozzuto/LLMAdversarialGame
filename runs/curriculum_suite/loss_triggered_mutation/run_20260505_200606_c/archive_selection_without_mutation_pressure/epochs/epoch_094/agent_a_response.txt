def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = p[0], p[1]
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a target resource:
    # 1) Prefer resources we are closer to than opponent (margin).
    # 2) If opponent can grab them next (opp dist <=1), avoid; deny by seeking resources we can reach first.
    scored = []
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        margin = do - ds
        opp_next = (do <= 1)
        danger = 1 if opp_next and ds >= do else 0
        # Higher is better; strong discourage if opponent likely to grab next.
        scored.append((-(margin), -ds, danger, rx, ry))

    # Sort by: maximize margin (so use negative margin in primary), but penalize danger
    scored.sort(key=lambda t: (t[2], t[0], t[1]))
    # Find best feasible candidate under "deny next-grab"
    target = None
    for m in scored:
        rx, ry = m[3], m[4]
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        if do <= 1 and ds >= do:
            continue
        target = (rx, ry)
        break
    if target is None:
        # fallback: pick resource where opponent is closest (to potentially contest/deny)
        target = min(resources, key=lambda p: (man(ox, oy, p[0], p[1]), man(sx, sy, p[0], p[1])))

    tx, ty = target

    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        ds_t = man(nx, ny, tx, ty)
        do_t = man(ox, oy, tx, ty)
        # Evaluate using chosen target but also add a "kite" term against denier
        opp_d_after = man(nx, ny, ox, oy)

        # If moving closer to target doesn't beat opponent's reach, prefer kiting
        beat = 1 if ds_t < do_t else 0
        # Also avoid steps that allow opponent to immediately reach target while we fall behind
        opp_can_next = 1 if do_t <= 1 else 0
        risk = opp_can_next and (ds_t >= do_t)

        # Main: minimize ds_t; secondary: maximize beat and kite
        val = -ds_t
        val += 50 * beat
        val += 0.5 * opp_d_after
        if (nx, ny) == (tx, ty):
            val += 1000000
        if risk:
            val -= 200

        if val > best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]]