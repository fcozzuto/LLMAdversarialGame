def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    # Prefer resources we can secure strictly earlier than opponent (interception bias)
    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    feasible = []
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        margin = od - sd
        if margin >= 1:
            # earlier is better; also prefer resources closer to us to reduce path variance
            feasible.append((sd, -margin, rx, ry))
    if feasible:
        feasible.sort()
        _, _, tx, ty = feasible[0]
    else:
        # If we can't secure any first, move to a resource that is "most contested":
        # minimize (sd - od) i.e., closest to opponent while still not too far from us.
        best = None
        for rx, ry in resources:
            sd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            # smaller value => more likely to create tie or steal later
            val = (sd - od, sd, rx, ry)
            if best is None or val < best[0]:
                best = (val, rx, ry)
        _, tx, ty = best[0][0], best[1], best[2]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs:
        return [int(dx), int(dy)]

    # Deterministic fallback: try axis steps then stay
    candidates = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    for mdx, mdy in candidates:
        nx, ny = sx + mdx, sy + mdy
        if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs:
            return [int(mdx), int(mdy)]
    return [0, 0]