def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    best = None  # (adv_key, tx, ty) where adv_key smaller is better
    for rx, ry in resources:
        my = man(sx, sy, rx, ry)
        ot = man(ox, oy, rx, ry)
        # Prefer being closer; if behind, minimize how far and still aim for nearer-to-opponent targets.
        if my <= ot:
            adv = ot - my
            key = (0, -adv, my, rx, ry)
        else:
            # behind: try to reduce distance gap and keep target not too far from opponent
            key = (1, my - ot, ot, my, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best

    step_options = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            step_options.append((dx, dy))
    step_options.append((0, 0))

    chosen = None  # (move_key, dx, dy)
    for dx, dy in step_options:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)

        # If stepping can change which resource is most attractive, estimate using the top few.
        # Keep it light/deterministic: evaluate only current target and nearest alternative by simple metric.
        alt = None
        best_alt_key = None
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            a_my = man(nx, ny, rx, ry)
            a_ot = man(ox, oy, rx, ry)
            # advantage heuristic
            if a_my <= a_ot:
                a_key = (0, -(a_ot - a_my), a_my, rx, ry)
            else:
                a_key = (1, (a_my - a_ot), a_ot, a_my, rx, ry)
            if best_alt_key is None or a_key < best_alt_key:
                best_alt_key = a_key
                alt = (rx, ry)
        alt_myd = man(nx, ny, alt[0], alt[1]) if alt else myd

        # Move key: maximize chance to collect (min myd), avoid giving opponent edge (increase their relative disadvantage)
        # and prefer progress over staying still.
        move_key = (
            myd,                          # nearer to chosen target is best
            -max(0, opd - myd),          # prefer moves that reduce opponent advantage (or create ours)
            alt_myd,                      # also consider alt pickup feasibility
            0 if (dx == 0 and dy == 0) else 1,
            abs(dx) + abs(dy),           # slight tie-break to avoid zigzag
            tx, ty, dx, dy
        )
        if chosen is None or move_key < chosen[0]:
            chosen = (move_key, dx, dy)

    # If all moves blocked (unlikely), stay.
    if chosen is None:
        return [0, 0]
    return [int(chosen[1]), int(chosen[2])]