def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) or ("evader" in opp_role and "pursuer" in self_role) or ("pursuer" in self_role or opp_role == "pursuer")

    moves = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def blocked_neighbors(x, y):
        # Penalize moving into tight spots near obstacles to reduce zigzag trapping.
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs:
                cnt += 1
        return cnt

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # When pursuing: go closer, prefer moves that reduce distance while not stepping into obstacle-tight cells.
        # When evading: go farther, but anchor toward a far corner to counter zigzag.
        corner_far = max(manh(nx, ny, cx, cy) for cx, cy in corners)
        corner_near_opp = min(manh(nx, ny, cx, cy) for cx, cy in corners)
        tight = blocked_neighbors(nx, ny)

        if i_am_pursuer:
            val = d2 * 1.0 + tight * 0.75 + manh(nx, ny, (w-1)//2, (h-1)//2) * 0.05
            # Choose minimum deterministically; tie-break by lexicographic move order.
            if best_val is None or val < best_val:
                best_val = val
                best = [dx, dy]
        else:
            val = d2 * -1.0 + (-corner_far) * 0.15 + tight * 0.5 + corner_near_opp * 0.01
            # Choose maximum deterministically.
            if best_val is None or val > best_val:
                best_val = val
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best