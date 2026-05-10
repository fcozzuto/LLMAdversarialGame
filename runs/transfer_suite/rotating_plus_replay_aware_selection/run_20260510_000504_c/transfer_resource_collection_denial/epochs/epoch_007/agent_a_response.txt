def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def parse_resources():
        out = []
        for r in observation.get("resources", []) or []:
            if isinstance(r, dict):
                if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                    out.append((int(r["position"][0]), int(r["position"][1])))
                elif "x" in r and "y" in r:
                    out.append((int(r["x"]), int(r["y"])))
            elif isinstance(r, (list, tuple)) and len(r) >= 2:
                out.append((int(r[0]), int(r[1])))
        return out
    res = parse_resources()
    if not res:
        return [0, 0]
    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    self_dists = [(man((sx, sy), t), t) for t in res if t not in obstacles]
    if not self_dists:
        return [0, 0]
    self_dists.sort()
    my_near = self_dists[0][1]
    opp_dists = [(man((ox, oy), t), t) for t in res if t not in obstacles]
    opp_dists.sort()
    opp_near = opp_dists[0][1]
    # predict opponent next position by greedy move to its nearest target
    def step_towards(x, y, tx, ty):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return (x, y)
        return (nx, ny)
    pred_ox, pred_oy = step_towards(ox, oy, opp_near[0], opp_near[1])
    # choose our move to beat predicted opponent on some target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_key = None
    best_move = (0, 0)
    # scoring: prefer targets where we arrive no later than opponent and also reduce our distance
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        key = None
        local_best = None
        for t in res:
            if t in obstacles:
                continue
            d_me = man((nx, ny), t)
            d_opp = man((pred_ox, pred_oy), t)
            # tie-break: points by collecting first; prefer larger lead, then shorter time, then closer to my_near
            lead = d_opp - d_me
            k = (lead, -d_me, -man(t, my_near), -t[1], -t[0])
            if key is None or k > key:
                key = k
                local_best = t
        # if we can't beat anyone, still minimize our distance to nearest
        if local_best is None:
            local_best = my_near
            key = (man((pred_ox, pred_oy), local_best) - man((nx, ny), local_best), -man((nx, ny), local_best), 0, 0, 0)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]