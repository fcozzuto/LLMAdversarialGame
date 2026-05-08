def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx = int(sp[0]) if isinstance(sp, (list, tuple)) and len(sp) > 0 else 0
    sy = int(sp[1]) if isinstance(sp, (list, tuple)) and len(sp) > 1 else 0
    ox = int(op[0]) if isinstance(op, (list, tuple)) and len(op) > 0 else w - 1
    oy = int(op[1]) if isinstance(op, (list, tuple)) and len(op) > 1 else h - 1

    def to_points(v):
        pts = []
        if not v:
            return pts
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                pts.append((int(p[0]), int(p[1])))
        return pts

    obstacles = set(to_points(observation.get("obstacles")))
    opp_terr = set(to_points(observation.get("opponent_territory")))
    unclaimed = to_points(observation.get("unclaimed_cells"))

    deltas = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best = None
    bestv = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        v = 0
        if (nx, ny) in opp_terr:
            v += 20
        if (nx, ny) in set(unclaimed) if unclaimed else False:
            v += 50
        if unclaimed:
            # reward closeness to nearest unclaimed
            md = 10**18
            for cx, cy in unclaimed[:200]:
                d = dist2(nx, ny, cx, cy)
                if d < md:
                    md = d
            if md < 10**18:
                v += 10 - md // 10
        # slight preference toward opponent to contest
        v += -dist2(nx, ny, ox, oy) // 50

        if best is None or v > bestv:
            best = (dx, dy)
            bestv = v

    if best is None:
        # deterministic fallback: any valid non-obstacle in deltas order
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [int(dx), int(dy)]
        return [0, 0]

    return [int(best[0]), int(best[1])]