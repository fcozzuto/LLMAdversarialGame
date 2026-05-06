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

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    me = (sx, sy)
    opp = (ox, oy)

    # Pick a resource where we have relative advantage; deterministic tie-breaks.
    best = None
    for r in resources:
        ds = man(me, r)
        do = man(opp, r)
        # Prefer winning races (do - ds positive), then nearer resources.
        # Slight tie-break by coordinates for determinism.
        score = (do - ds) * 100 - ds - (r[0] * 0.01 + r[1] * 0.001)
        if best is None or score > best[0]:
            best = (score, r)
    target = best[1]

    # Choose next move that best reduces distance to target while avoiding obstacles.
    best_move = [0, 0]
    best_eval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            evalv = 10**9
        else:
            evalv = man((nx, ny), target)
            # If opponent is close to target, prefer moves that keep advantage growing.
            evalv += 0.05 * max(0, man((nx, ny), target) - man(me, target))
            # Deterministic tie-break: lexicographic on move
            evalv += (0.0001 * (dx + 1) + 0.00001 * (dy + 1))
        if best_eval is None or evalv < best_eval:
            best_eval = evalv
            best_move = [dx, dy]

    return best_move