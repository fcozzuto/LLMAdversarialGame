def choose_move(observation):
    w, h = observation.get('grid_width', 8), observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))
    def cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    if resources:
        best = None
        for r in resources:
            r = tuple(r)
            if r in obstacles: 
                continue
            da = cheb((sx, sy), r)
            do = cheb((ox, oy), r)
            score = (do - da)  # prefer resources closer to us than them
            key = (score, -da, -do, r[0], r[1])
            if best is None or key > best[0]:
                best = (key, r)
        _, target = best
    else:
        target = (ox, oy)  # no resources: head to opponent to limit their options
    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    moves = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
    seen = set()
    out = None
    for mx, my in moves:
        if (mx, my) in seen: 
            continue
        seen.add((mx, my))
        nx, ny = sx + mx, sy + my
        if inb(nx, ny) and (nx, ny) not in obstacles:
            out = [mx, my]
            break
    if out is not None:
        return out
    # If blocked, pick any safe move minimizing distance to target
    cand = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if inb(nx, ny) and (nx, ny) not in obstacles:
                dist = max(abs(nx-tx), abs(ny-ty))
                cand.append((dist, nx, ny, mx, my))
    cand.sort()
    return [cand[0][3], cand[0][4]] if cand else [0, 0]