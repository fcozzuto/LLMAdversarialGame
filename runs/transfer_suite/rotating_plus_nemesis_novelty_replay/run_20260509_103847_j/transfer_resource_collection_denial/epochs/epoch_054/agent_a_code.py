def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick best contest/collection target: prefer resources where we are closer (ds small) and opponent is farther (do large).
    best_score = None
    tx = ty = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Primary: maximize (do - ds) so we are the likely collector; Secondary: minimize our distance; Tertiary: deterministic.
        sc = (-(do - ds), ds, rx, ry)
        if best_score is None or sc < best_score:
            best_score = sc
            tx, ty = rx, ry

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Move greedily toward target with obstacle-aware tie-break.
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        blocked = (nx, ny) in obstacles
        # Prefer unblocked, then closer to target. Also slight preference to increase distance from opponent to reduce denial pressure.
        ds2 = man(nx, ny, tx, ty)
        opp_d2 = man(nx, ny, ox, oy)
        sc = (blocked, ds2, -(opp_d2), dx, dy)
        if best is None or sc < best[0]:
            best = (sc, (dx, dy))

    if best is not None:
        return [best[1][0], best[1][1]]

    # Fallback if all moves were somehow invalid (shouldn't happen).
    return [0, 0]