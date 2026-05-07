def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, dict):
            x = p.get("x", p.get("posx", p.get("position", (None, None))[0]))
            y = p.get("y", p.get("posy", p.get("position", (None, None))[1]))
        else:
            x, y = p[0], p[1]
        if x is not None and y is not None:
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, dict):
            x = r.get("x", r.get("posx", r.get("position", (None, None))[0]))
            y = r.get("y", r.get("posy", r.get("position", (None, None))[1]))
        else:
            x, y = r[0], r[1]
        if x is not None and y is not None:
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Target resources that we can reach sooner; penalize cells opponent is much closer to.
    best = None
    bestv = None
    for x, y in resources:
        sd = dist((sx, sy), (x, y))
        od = dist((ox, oy), (x, y))
        # Prefer winning races; add slight preference for nearer targets to get to collection sooner.
        v = (od - sd) * 100 - sd
        # If we can't win the race, still consider cells that are closest to us.
        if best is None or v > bestv or (v == bestv and (sd < dist((sx, sy), best))):
            best = (x, y)
            bestv = v

    tx, ty = best
    if tx == sx and ty == sy:
        return [0, 0]

    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obs or nx < 0 or nx >= w or ny < 0 or ny >= h:
        # Deterministically fall back to axis move that reduces distance most.
        cands = []
        for ddx, ddy in ((dx, 0), (0, dy), (0, 0), (-dx, 0), (0, -dy)):
            mx, my = sx + ddx, sy + ddy
            if 0 <= mx < w and 0 <= my < h and (mx, my) not in obs:
                cands.append((max(abs(tx - mx), abs(ty - my)), ddx, ddy))
        cands.sort()
        return [int(cands[0][1]), int(cands[0][2])] if cands else [0, 0]

    return [int(dx), int(dy)]