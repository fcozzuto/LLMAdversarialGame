def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))
        elif isinstance(p, dict):
            pos = p.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                blocked.add((pos[0], pos[1]))

    def parse_pos(v):
        if isinstance(v, dict):
            pos = v.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                return (pos[0], pos[1])
        elif isinstance(v, (list, tuple)) and len(v) >= 2:
            return (v[0], v[1])
        return None

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        p = parse_pos(r)
        if p and inb(p[0], p[1]) and p not in blocked:
            targets.append(p)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not targets:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                return [dx, dy]
        return [0, 0]

    def best_for(nx, ny):
        md = 10**9
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < md:
                md = d
        od = abs(ox - nx) + abs(oy - ny)
        return (-md * 1000) + od

    best = None
    best_sc = -10**30
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        sc = best_for(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    return best if best is not None else [0, 0]