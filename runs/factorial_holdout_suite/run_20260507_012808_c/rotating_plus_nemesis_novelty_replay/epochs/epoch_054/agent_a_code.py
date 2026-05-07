def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestscore = None
    def dist(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y
    for dx, dy in moves:
        nx = sx + dx; ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        if res:
            md = None
            for rx, ry in res:
                dd = dist(nx, ny, rx, ry)
                if md is None or dd < md:
                    md = dd
            if md is None:
                md = 10**9
        else:
            cx = w // 2; cy = h // 2
            md = dist(nx, ny, cx, cy)
        od = dist(nx, ny, ox, oy)
        score = md * 10 - od
        key = (score, dx, dy)
        if bestscore is None or key < bestscore:
            bestscore = key
            best = [dx, dy]
    if best is not None:
        return best
    return [0, 0]