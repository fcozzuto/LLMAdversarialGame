def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def clamp_step(v):
        return -1 if v < 0 else (1 if v > 0 else 0)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    unclaimed = observation.get("unclaimed_cells") or []
    if not unclaimed:
        # fallback: expand toward any known empty (not in territories) by using unclaimed if missing
        target = (w // 2, h // 2)
    else:
        # score unclaimed: near self, far from opponent, and prefer not-too-distant "approach"
        best = None
        bestv = -10**18
        for p in unclaimed:
            if not p or len(p) < 2:
                continue
            x, y = int(p[0]), int(p[1])
            if not valid(x, y):
                continue
            ds = (x - sx) * (x - sx) + (y - sy) * (y - sy)
            do = (x - ox) * (x - ox) + (y - oy) * (y - oy)
            # encourage moving toward opponent-sparse zones and avoiding being close to them
            v = (do - 0.7 * ds) - 0.05 * (x + y) + 0.02 * (x - y)
            if v > bestv:
                bestv = v
                best = (x, y)
        if best is None:
            target = (w // 2, h // 2)
        else:
            target = best

    tx, ty = target
    dx = clamp_step(tx - sx)
    dy = clamp_step(ty - sy)

    # diagonal-first attempt; if blocked/invalid, try axis moves toward target deterministically
    cand = []
    if dx != 0 and dy != 0:
        cand.append((dx, dy))
    cand.append((dx, 0))
    cand.append((0, dy))
    cand.append((0, 0))

    for ddx, ddy in cand:
        nx, ny = sx + ddx, sy + ddy
        if valid(nx, ny):
            return [ddx, ddy]

    return [0, 0]