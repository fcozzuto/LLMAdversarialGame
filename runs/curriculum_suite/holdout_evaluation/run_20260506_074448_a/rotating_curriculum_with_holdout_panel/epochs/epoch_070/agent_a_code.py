def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    # Identify opponent's likely target: nearest available resource.
    # Break ties deterministically by (distance, x, y).
    avail = [tuple(r) for r in resources if tuple(r) not in obstacles]
    if not avail:
        return [0, 0]
    opp_target = min(avail, key=lambda r: (man(ox, oy, r[0], r[1]), r[0], r[1]))
    tx, ty = opp_target
    opp_tdist = man(ox, oy, tx, ty)

    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Anticipatory intercept: score best resource by (how much we can beat opponent),
        # but prioritize resources near the opponent's target to deny tempo.
        myd_to_target = man(nx, ny, tx, ty)
        s = 0.0
        for rx, ry in avail:
            md = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Beat opponent / contest:
            if md < od:
                s += 4.0 + (od - md) * 1.5
            elif md == od:
                s += 1.2
            else:
                s -= (md - od) * 1.1

            # Deny opponent by moving into their likely corridor:
            s -= 0.12 * man(nx, ny, tx, ty)
            # Prefer moves that reduce distance to resources that opponent is far from
            # (to avoid purely shadowing opponent's safe collection).
            if od > opp_tdist:
                s += 0.35

        # Secondary tie-breaks: closer to opponent target (intercept) then closer to nearest resource.
        nearest = min(mandist for mandist in [man(nx, ny, r[0], r[1]) for r in avail])
        key = (-s, myd_to_target, nearest, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]