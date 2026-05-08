def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) and ("pursuer" not in role)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    escape_corner = max(corners, key=lambda c: max(abs(c[0]-ox), abs(c[1]-oy)))

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked: 
            return -10**9 if is_evader else 10**9

        d_after = max(abs(nx-ox), abs(ny-oy))
        if is_evader:
            ecx, ecy = escape_corner
            toward = (abs(nx-ox) - abs(sx-ox)) + (abs(ny-oy) - abs(sy-oy))
            # Prefer heading toward the escape corner (deterministic, no history)
            prog = - (abs(ecx-nx) + abs(ecy-ny))
            # Obstacle-aware local freedom
            mob = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if inside(tx, ty) and (tx, ty) not in blocked: mob += 1
            return d_after * 10 + prog * 1.5 + mob * 0.2 + toward * 0.1
        else:
            # Pursuer: minimize distance while preferring moves that don't get cornered by obstacles
            # Greedy one-step lookahead: also favor reducing both coordinates where possible.
            dist = d_after
            reduce_axis = - (abs(nx-ox) + abs(ny-oy))  # larger is better (less sum)
            # Count available exits from next cell
            mob = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if inside(tx, ty) and (tx, ty) not in blocked: mob += 1
            return -dist * 10 + reduce_axis * 0.5 + mob * 0.1

    best = None
    best_sc = None
    for dx, dy in moves:
        sc = score_move(dx, dy)
        if best_sc is None or (sc > best_sc) or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]