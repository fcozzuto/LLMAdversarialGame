def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)

    # Pick a target we can beat (deterministic), favor closer by tradeoff.
    best = None
    best_key = None
    for rx, ry in resources:
        dme = man(me, (rx, ry))
        dop = man(opp, (rx, ry))
        # advantage: higher means better; deterministic tie-breakers
        adv = dme - dop
        # also prefer not-too-far overall and prefer resources on our "front"
        front = (rx + (h - 1 - ry)) if (sx <= w//2) else ((w - 1 - rx) + ry)
        key = (adv, dme, -front, rx, ry)
        if best_key is None or key < best_key:
            best_key, best = key, (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Choose step maximizing "progress" and immediate safety (avoid moving into obstacles if possible).
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        d1 = man((nx, ny), (tx, ty))
        d0 = man(me, (tx, ty))
        # Predict whether we gain relative advantage vs opponent target quickly.
        # Also mildly avoid getting too close to opponent.
        opp_d = man((nx, ny), opp)
        score = (-(d1), (d0 - d1), -abs(d1 - 0), -opp_d // 3, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_score is None or score > best_score:
            best_score, best_move = score, (dx, dy)
    return [int(best_move[0]), int(best_move[1])]