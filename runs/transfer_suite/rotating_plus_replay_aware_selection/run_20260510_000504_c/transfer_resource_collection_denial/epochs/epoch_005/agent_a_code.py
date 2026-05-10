def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]

    obs = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                res.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                res.append((int(r["x"]), int(r["y"])))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
    if not res:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target deterministically: maximize "we are closer than opponent"
    best = None
    best_key = None
    for t in res:
        if t in obstacles:
            continue
        d1 = man((sx, sy), t)
        d2 = man((ox, oy), t)
        key = (d2 - d1, -d1, -d2, t[0], t[1])
        if best_key is None or key > best_key:
            best_key = key
            best = t
    if best is None:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = man((nx, ny), best)
        d_opp = man((ox, oy), best)
        # Prefer getting closer to target and preventing opponent advantage.
        score = (d_opp - d_self, -d_self, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move