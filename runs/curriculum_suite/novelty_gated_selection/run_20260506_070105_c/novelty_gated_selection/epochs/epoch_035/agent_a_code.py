def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except Exception:
        sx = sy = ox = oy = 0

    def parse_pos(p):
        if isinstance(p, dict):
            x = p.get("x", p.get("X", p.get("col", p.get("cx", 0))))
            y = p.get("y", p.get("Y", p.get("row", p.get("cy", 0))))
        else:
            try:
                x, y = p[0], p[1]
            except Exception:
                return None
        try:
            x, y = int(x), int(y)
        except Exception:
            return None
        if 0 <= x < w and 0 <= y < h:
            return (x, y)
        return None

    resources = []
    for r in (observation.get("resources", []) or []):
        rp = parse_pos(r)
        if rp is not None:
            resources.append(rp)

    obs = set()
    for o in (observation.get("obstacles", []) or []):
        op = parse_pos(o)
        if op is not None:
            obs.add(op)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if resources:
            rdist = min(md(nx, ny, rx, ry) for rx, ry in resources)
        else:
            rdist = 10**6
        odist = md(nx, ny, ox, oy)
        score = (-rdist * 1000) + (odist)  # prioritize resources, keep away from opponent
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]