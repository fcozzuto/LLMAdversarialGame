def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    rlist = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rlist.append((int(p[0]), int(p[1])))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in oset

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = -md(nx, ny, ox, oy) * 0.3
        if rlist:
            dr = min(md(nx, ny, rx, ry) for rx, ry in rlist if valid(rx, ry) or True)
            score -= dr
        for rx, ry in rlist:
            if nx == rx and ny == ry:
                score += 1000
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]