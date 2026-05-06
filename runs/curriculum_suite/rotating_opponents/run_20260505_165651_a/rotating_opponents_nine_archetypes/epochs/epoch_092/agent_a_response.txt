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

    def md(a, b, c, d):  # manhattan
        return abs(a - c) + abs(b - d)

    # Select target: maximize our tempo advantage; otherwise contest by minimizing worst arrival.
    best = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd  # positive => we arrive earlier
        # Primary: higher adv; Secondary: smaller our distance; Tertiary: farther from opponent (more separation).
        key = (adv, -sd, md(ox, oy, rx, ry))
        if best is None or key > best[0]:
            best = (key, (rx, ry), sd, od)
    _, (tx, ty), _, _ = best

    # Move one step toward target, but never into obstacles; choose among ties deterministically.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        # Prefer smaller distance to target; if equal, prefer increasing our arrival tempo vs opponent.
        d_self = md(nx, ny, tx, ty)
        d_opp = md(ox, oy, tx, ty)
        score = (-d_self, d_opp - d_self, abs(nx - tx) + abs(ny - ty))
        if bestm is None or score > bestm[0]:
            bestm = (score, (dx, dy))

    if bestm is None:
        return [0, 0]
    return [int(bestm[1][0]), int(bestm[1][1])]