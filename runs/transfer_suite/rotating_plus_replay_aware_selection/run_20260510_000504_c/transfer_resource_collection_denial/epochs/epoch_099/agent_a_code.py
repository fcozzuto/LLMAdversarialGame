def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obs.add((int(q[0]), int(q[1])))
            else:
                if "x" in p and "y" in p:
                    obs.add((int(p["x"]), int(p["y"])))
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                res.append((int(q[0]), int(q[1])))
            else:
                if "x" in r and "y" in r:
                    res.append((int(r["x"]), int(r["y"])))
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    def clamp(x, a, b):
        return a if x < a else (b if x > b else x)
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def step_cost(nx, ny):
        best = 10**9
        for rx, ry in res:
            d = (rx - nx) * (rx - nx) + (ry - ny) * (ry - ny)
            if d < best:
                best = d
        if best == 10**9:
            best = 0
        opp_d = abs(nx - ox) + abs(ny - oy)
        return best * 2 + opp_d
    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        sc = step_cost(nx, ny)
        if (nx, ny) == (ox, oy):
            sc -= 100000
        if sc < best_score:
            best_score = sc
            best_move = (dx, dy)
    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]