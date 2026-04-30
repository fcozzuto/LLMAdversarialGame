def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set()
    for x, y in obstacles:
        if 0 <= x < gw and 0 <= y < gh:
            obs.add((x, y))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    def best_target(mode):
        best = None
        best_sc = None
        for rx, ry in resources:
            if not inb(rx, ry) or (rx, ry) in obs:
                continue
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            lead = do - ds  # positive means we are closer
            if mode == "grab":
                if lead < 2:
                    continue
                # prefer big lead, then small ds
                sc = lead * 1000 - ds
                if best_sc is None or sc > best_sc or (sc == best_sc and (rx, ry) < best):
                    best_sc = sc
                    best = (rx, ry)
            else:
                # interfere: pick where opponent is most ahead (most negative lead)
                if lead > 0:
                    # if opponent not ahead, still allow but lower priority
                    sc = -lead - ds * 0.1
                else:
                    sc = (-lead) * 1000 - ds
                if best_sc is None or sc > best_sc or (sc == best_sc and (rx, ry) < best):
                    best_sc = sc
                    best = (rx, ry)
        return best

    target = best_target("grab")
    if target is None:
        target = best_target("interfere")
    if target is None:
        return [0, 0]

    tx, ty = target
    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = None

    # Prefer approaching target; if intercept mode, also keep distance from opponent.
    want_grab = (man(sx, sy, tx, ty) + 2 <= man(ox, oy, tx, ty))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if (nx, ny) == (ox, oy):
            # avoid stepping onto opponent unless still tied-break forces it; penalize
            penalty = 50
        else:
            penalty = 0

        d_to_t = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)

        # primary: minimize distance to target
        sc = -d_to_t * 10 - penalty

        # secondary: in interfere mode, maximize separation from opponent to avoid gifting them captures
        if not want_grab:
            sc += d_opp * 1.5
        else:
            # in grab mode, slightly prefer keeping opponent further too
            sc += d_opp * 0.3

        # deterministic tie-break: prefer lower dx, then lower dy
        if best_score is None or sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]