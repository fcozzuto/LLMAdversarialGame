def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, dict):
            x = p.get("x", p.get("posx", p.get("position", (None, None)) and p.get("position")[0]))
            y = p.get("y", p.get("posy", p.get("position", (None, None)) and p.get("position")[1]))
        else:
            x, y = p[0], p[1]
        if x is not None and y is not None:
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, dict):
            x = r.get("x", r.get("posx", r.get("position", (None, None))[0]))
            y = r.get("y", r.get("posy", r.get("position", (None, None))[1]))
        else:
            x, y = r[0], r[1]
        if x is not None and y is not None:
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b):
        return abs(a[0] - b[0]) if abs(a[0] - b[0]) > abs(a[1] - b[1]) else abs(a[1] - b[1])

    best_t = resources[0]
    best_val = -10**9
    for t in resources:
        d1 = cheb((sx, sy), t)
        d2 = cheb((ox, oy), t)
        val = (d2 - d1) * 10 - d1  # prefer resources we are closer to; deny if opponent is closer
        if val > best_val:
            best_val = val
            best_t = t
        elif val == best_val:
            if d1 < cheb((sx, sy), best_t):
                best_t = t

    tx, ty = best_t
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        myd = cheb((nx, ny), (tx, ty))
        opp_to_t_now = cheb((ox, oy), (tx, ty))
        oppd = cheb((ox, oy), (tx, ty))  # unchanged this turn; keep simple but deterministic
        # score: reduce our distance; if we can't, increase separation from opponent to help denial
        separation = cheb((nx, ny), (ox, oy))
        score = -myd * 20 + (separation if myd == cheb((sx, sy), (tx, ty)) else 0) + (opp_to_t_now - oppd)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]