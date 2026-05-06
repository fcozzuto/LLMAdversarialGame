def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def rep_cell(r):
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (q[0], q[1])
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return (r[0], r[1])
        return None

    rpos = []
    for r in resources:
        q = rep_cell(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)

    if not rpos:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        # Prefer stealing: maximize (opponent can reach earlier? -> we want ours earlier)
        # advantage = opp_dist - our_dist (larger means we can arrive sooner)
        # Tie-break: prioritize smaller our_dist, then larger advantage, then lex.
        best_adv = None
        best_our = None
        for rx, ry in rpos:
            our_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            adv = opp_d - our_d
            if best_adv is None or adv > best_adv or (adv == best_adv and our_d < best_our):
                best_adv, best_our = adv, our_d

        # Also prevent us from running away: if no positive advantage exists, fall back to minimizing our distance.
        opp_nearest = min(abs(nx - rx) + abs(ny - ry) for rx, ry in rpos)
        key = (-(best_adv if best_adv is not None else -999), best_our if best_our is not None else opp_nearest, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]