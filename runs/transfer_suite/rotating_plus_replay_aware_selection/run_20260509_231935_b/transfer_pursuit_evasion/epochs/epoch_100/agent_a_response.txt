def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    sr = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in sr) or ("pursue" in sr)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # Prefer staying central / line toward target deterministically
    pref = [(0,0),(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]
    order = [m for m in pref if m in moves] + [m for m in moves if m not in pref]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def manhattan(x, y, tx, ty):
        return abs(x - tx) + abs(y - ty)

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    # If evader: head to farthest corner from opponent, alternating slight bias by turn index.
    corners = [[0,0],[w-1,0],[0,h-1],[w-1,h-1]]
    best_corner = corners[0]
    best_d = -1
    for cx, cy in corners:
        d = manhattan(sx, sy, cx, cy)
        od = manhattan(ox, oy, cx, cy)
        # Favor corners far from opponent, also reachable
        score = (od, -d)
        if score > (best_d, 0):
            best_d = od
            best_corner = [cx, cy]
    tx, ty = best_corner[0], best_corner[1]
    if not is_pursuer and (observation.get("turn_index", 0) or 0) % 2 == 1:
        # small deterministic alternate target: the diagonally opposite corner
        alt = corners[1:] + corners[:1]
        for c in alt:
            if c != best_corner:
                tx, ty = c[0], c[1]
                break

    best_move = (0, 0)
    best_val = None

    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_to_opp = manhattan(nx, ny, ox, oy)
        f_nei = free_neighbors(nx, ny)

        if is_pursuer:
            # minimize distance; discourage moves into narrow spots
            val = (d_to_opp, -f_nei, abs(nx - sx) + abs(ny - sy))
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            # maximize distance; also prefer more available space and avoid shrinking to dead ends
            d_to_target = manhattan(nx, ny, tx, ty)
            val = (-d_to_opp, -f_nei, d_to_target)
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]