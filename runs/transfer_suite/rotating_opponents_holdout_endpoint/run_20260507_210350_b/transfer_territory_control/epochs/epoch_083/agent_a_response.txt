def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    target = None
    best_t = -10**18
    for x, y in unclaimed:
        if not inb(x, y) or (x, y) in obstacles:
            continue
        sd = md(x, y, sx, sy)
        od = md(x, y, ox, oy)
        # Aim for cells we can reach earlier, also slightly prefer expanding outward
        v = (od - sd) * 7 + (2 if (x, y) not in self_terr else -2) - (md(x, y, cx, cy) * 0.5)
        if v > best_t:
            best_t, target = v, (x, y)
    if target is None:
        # Fall back: chase opponent or nearest unclaimed-like area
        target = min(unclaimed or [(cx, cy)], key=lambda p: md(p[0], p[1], sx, sy))

    tx, ty = int(target[0]), int(target[1])
    best_m = [0, 0]
    best_v = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_t = md(nx, ny, tx, ty)
        d_opp = md(nx, ny, ox, oy)
        d_self = md(nx, ny, sx, sy)

        in_unclaimed = (nx, ny) in set(map(tuple, unclaimed)) if unclaimed else False
        # Encourage taking/contesting cells and reducing distance to target while denying opponent
        v = (d_opp - d_self) * 6 + (-d_to_t) * 2
        if (nx, ny) in self_terr:
            v -= 1
        if (nx, ny) in opp_terr:
            v += 4  # flipping on entry is enabled
        if in_unclaimed:
            v += 3

        # Mild preference toward center to avoid getting trapped at edges
        v -= (md(nx, ny, cx, cy) * 0.1)

        # Deterministic tie-breaker: smallest (dx,dy) in dirs order
        if v > best_v:
            best_v = v
            best_m = [dx, dy]
    return best_m