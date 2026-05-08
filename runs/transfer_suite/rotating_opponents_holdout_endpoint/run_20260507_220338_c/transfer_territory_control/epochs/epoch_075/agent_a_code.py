def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocks = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed_pts = []
    for p in unclaimed:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed_pts.append((x, y))

    scores = observation.get("scores") or {}
    s0 = scores.get("self", 0)
    s1 = scores.get("opponent", 0)
    try:
        s0 = float(s0)
    except:
        s0 = 0
    try:
        s1 = float(s1)
    except:
        s1 = 0

    attack = s0 >= s1

    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    bestv = -10**18

    def cell_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocks

    def nearest_dist2(px, py, pts):
        bd = 10**18
        for ax, ay in pts:
            dx, dy = px - ax, py - ay
            d = dx * dx + dy * dy
            if d < bd:
                bd = d
        return bd if bd != 10**18 else 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        v = 0
        if unclaimed_pts:
            v += 2000 - nearest_dist2(nx, ny, unclaimed_pts)
        dop = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if attack:
            v += 800 - dop // 2
        else:
            v += dop // 2
        v += (nx + ny) * 0.001  # deterministic tie-break
        if v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        for dx, dy in [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if cell_ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]