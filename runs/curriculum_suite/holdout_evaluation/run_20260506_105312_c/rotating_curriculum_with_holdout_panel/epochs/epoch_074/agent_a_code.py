def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    rlist = [(int(r[0]), int(r[1])) for r in resources if len(r) >= 2]
    rlist = [(rx, ry) for rx, ry in rlist if inb(rx, ry) and (rx, ry) not in obs]
    if not rlist:
        return [0, 0]

    opp_best = min(md(ox, oy, rx, ry) for rx, ry in rlist)
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_best = min(md(nx, ny, rx, ry) for rx, ry in rlist)

        # Heuristic: maximize advantage vs opponent's nearest-resource distance.
        # Add mild tie-breakers to prefer moves that reduce "second-best" options too.
        sorted_self = sorted(md(nx, ny, rx, ry) for rx, ry in rlist)
        second_self = sorted_self[1] if len(sorted_self) > 1 else sorted_self[0]

        value = (opp_best - self_best, -second_self, -md(nx, ny, ox, oy), -dx, -dy)
        if best is None or value > best[0]:
            best = (value, dx, dy)

    if best:
        return [best[1], best[2]]

    # Fallback: any valid move
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
    return [0, 0]