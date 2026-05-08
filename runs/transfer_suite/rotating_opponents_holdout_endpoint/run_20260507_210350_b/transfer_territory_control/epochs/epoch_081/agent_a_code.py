def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y, tx, ty):
        d1 = abs(x - tx) + abs(y - ty)
        d2 = (x - tx) * (x - tx) + (y - ty) * (y - ty)
        return (d1, d2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    opp_front = set()
    seeds = opp_terr if opp_terr else {(ox, oy)}
    for px, py in seeds:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = px + dx, py + dy
                    if (nx, ny) in unclaimed:
                        opp_front.add((nx, ny))

    if opp_front:
        candidates = opp_front
    else:
        boundary = [c for c in unclaimed if c[0] in (0, w - 1) or c[1] in (0, h - 1)]
        if boundary:
            candidates = boundary
        else:
            candidates = list(unclaimed) if unclaimed else [(sx, sy)]

    tx, ty = min(candidates, key=lambda p: (dist(sx, sy, p[0], p[1]), p[0], p[1]))

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = dist(nx, ny, tx, ty)
        on_self = 0 if (nx, ny) in self_terr else 1
        on_unclaimed = 0 if (nx, ny) in unclaimed else 1
        val = (d, on_unclaimed, on_self, dx, dy)
        if best is None or val < best[0]:
            best = (val, [dx, dy])

    return best[1] if best is not None else [0, 0]