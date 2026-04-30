def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            ex, ey = int(o[0]), int(o[1])
            if 0 <= ex < w and 0 <= ey < h:
                obstacles.add((ex, ey))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_overall = (-10**18, 0, 0)
    # Strategy: maximize our distance advantage to resources; if none, minimize opponent closeness.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # compute best advantage from (nx,ny)
        best_adv = -10**18
        best_dist_self = 10**18
        best_dist_opp = 10**18
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            adv = do - ds  # positive if we are closer
            if adv > best_adv or (adv == best_adv and (ds < best_dist_self or (ds == best_dist_self and do < best_dist_opp))):
                best_adv, best_dist_self, best_dist_opp = adv, ds, do

        # choose score:
        # - if we can be closer (best_adv>0), strongly prefer that resource
        # - otherwise, still choose move that maximizes adv (closest to us, but also "far" from opponent)
        if best_adv > 0:
            val = 10.0 * best_adv - 0.5 * best_dist_self + 0.05 * best_dist_opp
        else:
            val = 2.0 * best_adv - 0.25 * best_dist_self + 0.02 * best_dist_opp

        # tiny deterministic tie-break to reduce oscillations: prefer smaller dx, then dy, then stay
        tie = (abs(dx) + abs(dy), dx, dy)
        val = val - 1e-6 * tie[0]

        if val > best_overall[0]:
            best_overall = (val, dx, dy)
    return [int(best_overall[1]), int(best_overall[2])]