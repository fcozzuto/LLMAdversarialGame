def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def tie_break_score(x, y):
        # deterministic bias toward center and away from corners
        cx, cy = (w-1)/2.0, (h-1)/2.0
        return - (abs(x-cx) + abs(y-cy))

    # Choose a target resource: maximize (opp_distance - self_distance) with small tie-break
    best_t = None
    best_adv = -10**18
    for rx, ry in resources:
        d_my = dist((sx, sy), (rx, ry))
        d_opp = dist((ox, oy), (rx, ry))
        adv = d_opp - d_my
        if adv > best_adv or (adv == best_adv and (rx+ry) < (best_t[0]+best_t[1] if best_t else 10**9)):
            best_adv = adv
            best_t = (rx, ry)

    # If no meaningful advantage (or no resources), just chase nearest resource without opponent awareness
    if best_t is None:
        # move toward center if possible
        tx, ty = (w-1)//2, (h-1)//2
        best = [0, 0]
        best_sc = -10**18
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if not ok(nx, ny): 
                continue
            sc = tie_break_score(nx, ny) - (abs(nx-tx)+abs(ny-ty))
            if sc > best_sc:
                best_sc = sc
                best = [dx, dy]
        return best

    tx, ty = best_t
    # Move that maximizes next-step advantage versus opponent on this target,
    # while penalizing proximity to obstacles and discouraging letting opponent get closer.
    best_move = [0, 0]
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx+dx, sy+dy
        if not ok(nx, ny):
            continue
        d_my_next = dist((nx, ny), (tx, ty))
        d_opp = dist((ox, oy), (tx, ty))
        adv_next = d_opp - d_my_next

        # obstacle safety: avoid stepping near obstacles (strongly avoid adjacency)
        obst_pen = 0
        for ex, ey in obstacles:
            d = abs(nx-ex) + abs(ny-ey)
            if d == 0:
                obst_pen = 10**9
                break
            if d == 1:
                obst_pen += 7
            elif d == 2:
                obst_pen += 2

        # ensure we are not moving away from target when we could approach
        d_cur = dist((sx, sy), (tx, ty))
        approach_bonus = (d_cur - d_my_next)

        sc = 1000 * adv_next + 5 * approach_bonus - obst_pen + 0.01 * tie_break_score(nx, ny)

        # slight extra rule: if opponent is adjacent to the target, prioritize blocking approach by reducing their distance
        d_opp_cur = dist((ox, oy), (tx, ty))
        if d_opp_cur <= 2:
            sc -= 0.5 * d_my_next  # keep yourself closer when contest is hot

        if sc > best_sc:
            best_sc = sc
            best_move = [dx, dy]

    return best_move