def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Deterministic retreat/advance toward opponent side corner to break stagnation
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1
        bestd = 10**9
        best = [0, 0]
        for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < bestd:
                    bestd = d
                    best = [dx, dy]
        return best

    # Utility: pick next step that improves relative advantage over opponent for the best contestable resource
    best_move = [0, 0]
    best_val = -10**18
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Encourage moving off obstacles-adjacent "trap" cells
        trap = 0
        for ax, ay in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            if legal(nx + ax, ny + ay) and (nx + ax, ny + ay) in obstacles:
                trap += 1

        # Choose best resource for which we have the largest lead (or smallest deficit)
        best_res_val = -10**18
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Lead is (do - ds): positive means we get there earlier
            lead = do - ds
            # Slight preference for closer immediate pickup and for increasing lead
            v = lead * 10 - ds - 2 * trap
            if v > best_res_val:
                best_res_val = v

        # Tie-break deterministically: prefer smaller ds to that best resource and then lexicographic move
        # Compute ds for tie-break cheaply using the resource that maximizes v again
        # (still deterministic and small: <=12 resources)
        if best_res_val > best_val:
            best_val = best_res_val
            best_move = [dx, dy]
        elif best_res_val == best_val:
            # Tie-break
            cand = [dx, dy]
            bestcand = best_move
            if (cand[0], cand[1]) < (bestcand[0], bestcand[1]):
                best_move = cand

    return best_move