def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_set = set()
    for t in observation.get("obstacles") or []:
        try:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except:
            pass

    resources = []
    for t in observation.get("resources") or []:
        try:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                resources.append((x, y))
        except:
            pass
    if not resources:
        return [0, 0]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a resource we can contest: prefer being closer, then shorter distance, then upper-left tie.
    best = None
    best_key = None
    for rx, ry in resources[:12]:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # Small bias toward collecting earlier (closer overall) and toward center.
        center_bias = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        key = (-(1 if ds < do else 0), ds - do, ds, center_bias, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Evaluate next move among 9 deltas; obstacles are handled by letting engine keep us in place.
    deltas = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    best_m = None
    best_m_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        # If we'd step into obstacle, treat as landing worse.
        if (nx, ny) in obs_set:
            continue

        ds = manh(nx, ny, tx, ty)
        do = manh(ox, oy, tx, ty)

        # Check whether this move grabs the target.
        grab = 1 if (nx, ny) == (tx, ty) else 0

        # Avoid getting too close to opponent when not grabbing.
        prox_opp = manh(nx, ny, ox, oy)
        opp_penalty = 0
        if not grab:
            opp_penalty = -min(prox_opp, 6)

        # Mild preference to move toward target along correct direction.
        toward = -((tx - nx) * (tx - sx) + (ty - ny) * (ty - sy))

        # Deterministic tie-break by delta ordering: prefer (0,0), then right, up, etc.
        delta_order = (dx, dy)

        key = (-grab, (ds - do), ds, opp_penalty, toward, delta_order)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    dx, dy = best_m
    return [int(dx), int(dy)]