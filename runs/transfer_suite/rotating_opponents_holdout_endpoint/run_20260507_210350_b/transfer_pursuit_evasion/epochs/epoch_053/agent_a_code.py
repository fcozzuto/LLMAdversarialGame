def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", None)
    if resources is None:
        resources = observation.get("resource_positions", None)
    if resources is None:
        resources = []
    resources = [tuple(p) for p in (resources or [])]
    sc = observation.get("scores", None)
    s_self = sc[0] if isinstance(sc, (list, tuple)) and len(sc) > 0 else 0
    s_opp = sc[1] if isinstance(sc, (list, tuple)) and len(sc) > 1 else 0
    attack = s_self <= s_opp
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def best_res_dist(x, y):
        if not resources: return 999
        bd = 999
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < bd: bd = d
            if bd == 0: return 0
        return bd
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = -10**18
    parity = (observation.get("turn_index", 0) or 0) & 1
    if parity:
        moves = [moves[4]] + moves[:4] + moves[5:]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        rd = best_res_dist(nx, ny)
        od = cheb(nx, ny, ox, oy)
        obs_pen = 0
        for ax, ay in obstacles:
            d = cheb(nx, ny, ax, ay)
            if d == 0:
                obs_pen = 10000
                break
            if d == 1: obs_pen += 180
            elif d == 2: obs_pen += 50
            elif d == 3: obs_pen += 10
        v = 0
        v += (200 - 60 * rd) if rd < 999 else -300
        if attack:
            v += 120 - 30 * od
        else:
            v += od
        v -= obs_pen
        if v > bestv or (v == bestv and (best is None or (dx, dy) < best)):
            bestv = v
            best = (dx, dy)
    if best is None:
        best = (0, 0)
    return [int(best[0]), int(best[1])]