def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    resources = observation.get("resources", []) or []
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obs
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if resources:
        def score_cell(x, y, r):
            return abs(r[0] - x) + abs(r[1] - y)
        tx, ty = min(resources, key=lambda r: (score_cell(sx, sy, r), r[0], r[1]))[0:2]
    else:
        tx, ty = (w - 1 if sx <= w // 2 else 0, h - 1 if sy <= h // 2 else 0)
    def step(a, b):
        if b > a: return 1
        if b < a: return -1
        return 0
    dx0, dy0 = step(sx, tx), step(sy, ty)
    cand = []
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if valid(nx, ny):
            dcur = abs(nx - tx) + abs(ny - ty)
            dopp = abs(nx - ox) + abs(ny - oy)
            cand.append((dcur, -dopp, mdx, mdy))
    if not cand:
        return [0, 0]
    cand.sort()
    best = cand[0]
    return [int(best[2]), int(best[3])]