def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position", None)
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    if not targets:
        return [0, 0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy

        my_pos = (nx, ny)
        # Advantage over opponent: smaller dist to a resource than opponent by a margin
        best_adv = None
        best_my = None
        for tx, ty in targets:
            rpos = (tx, ty)
            dm = dist(my_pos, rpos)
            do = dist((ox, oy), rpos)
            adv = dm - do  # negative means we are closer
            if best_adv is None or adv < best_adv or (adv == best_adv and dm < best_my):
                best_adv = adv
                best_my = dm

        # Prefer breaking ties deterministically: smaller best_adv, then closer to that target,
        # then avoid staying put only if otherwise equal.
        stay_pen = 1 if (dx == 0 and dy == 0 and legal(sx, sy)) else 0
        score = (best_adv, best_my, stay_pen)

        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]