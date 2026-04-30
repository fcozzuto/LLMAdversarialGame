def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def manh(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    if resources:
        best_moves = []
        for dx, dy, nx, ny in legal:
            best_val = -10**18
            best_res = None
            for rx, ry in resources:
                myd = manh(nx, ny, rx, ry)
                opd = manh(ox, oy, rx, ry)
                # Prefer resources where I'm closer than opponent; strong lead beats small lead.
                val = (opd - myd) * 1000 - myd
                # Slightly prefer targets not "behind" me (adds determinism)
                val += 0.1 * (opd % 7) - 0.1 * (myd % 5)
                if val > best_val:
                    best_val = val
                    best_res = (rx, ry)
            best_moves.append((best_val, best_res, dx, dy, nx, ny))
        best_moves.sort(key=lambda t: (-t[0], manh(t[4], t[5], t[1][0], t[1][1]) if t[1] else 0, t[2], t[3]))
        return [int(best_moves[0][2]), int(best_moves[0][3])]

    # No resources: move toward center while staying away from opponent.
    cx, cy = w // 2, h // 2
    best = None
    for dx, dy, nx, ny in legal:
        to_center = manh(nx, ny, cx, cy)
        away = manh(nx, ny, ox, oy)
        val = away * 10 - to_center
        cand = (val, dx, dy)
        if best is None or cand > best:
            best = cand
    return [int(best[1]), int(best[2])]