def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cand = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                myd = man(sx, sy, x, y)
                oppd = man(ox, oy, x, y)
                margin = oppd - myd
                center = abs(x - (w - 1) / 2.0) + abs(y - (h - 1) / 2.0)
                score = (margin * 100) - myd - 0.05 * center - (0 if margin > 0 else 25)
                cand.append((score, x, y, myd, oppd, margin))
    if not cand:
        return [0, 0]

    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, tx, ty, myd, oppd, margin = cand[0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                d = man(nx, ny, tx, ty)
                # Prefer moves that keep/extend race advantage; deterministic tie-break by position.
                race = (man(ox, oy, tx, ty) - d)
                moves.append((d, -race, nx, ny, dx, dy))
    if not moves:
        return [0, 0]

    moves.sort(key=lambda m: (m[0], m[1], m[2], m[3], m[4], m[5]))
    return [moves[0][4], moves[0][5]]