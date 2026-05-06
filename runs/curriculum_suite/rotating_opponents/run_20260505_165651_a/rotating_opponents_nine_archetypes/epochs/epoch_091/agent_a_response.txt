def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # New strategy: choose a resource where we have a *tempo advantage* over the opponent.
    best_t = None
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        tempo = od - sd  # higher means we get there sooner
        # tie-break: prefer closer overall and farther from opponent so we don't "lead them"
        t = (-(tempo), sd, dist(ox, oy, rx, ry), rx, ry)
        if best_t is None or t < best_t[0]:
            best_t = (t, (rx, ry))

    target = best_t[1]
    tx, ty = target

    # Step toward target while also avoiding giving the opponent easy access: maximize next opp distance.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_to = dist(nx, ny, tx, ty)
        opp_to = dist(nx, ny, ox, oy)
        # primary: reduce self distance to target; secondary: keep away from opponent; tertiary: avoid stepping "closer" to opponent-target line
        key = (self_to, -opp_to, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    return [best[1][0], best[1][1]] if best else [0, 0]