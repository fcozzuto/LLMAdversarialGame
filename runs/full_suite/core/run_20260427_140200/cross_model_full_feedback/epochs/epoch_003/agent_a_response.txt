def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by): return max(abs(ax - bx), abs(ay - by))
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    # If resources exist, aim for a resource where we get a distance advantage over the opponent.
    if resources:
        best_move = (0, 0)
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # For this next position, consider the best resource (we want the one giving max advantage).
            best_r_score = None
            best_r_my = None
            for r in resources:
                rx, ry = r[0], r[1]
                dm = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Negative means we're closer than opponent; prioritize most negative (largest advantage).
                adv = dm - do
                if best_r_score is None or adv < best_r_score or (adv == best_r_score and dm < best_r_my):
                    best_r_score = adv
                    best_r_my = dm
            # Prefer stronger advantage; tie-break by smaller distance to that resource; then avoid staying.
            stay_pen = 1 if (dx == 0 and dy == 0) else 0
            val = (best_r_score, best_r_my, stay_pen)
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move to reduce distance to opponent (so they can't easily farm when resources appear)
    # while avoiding obstacles.
    best_move = (0, 0)
    best_d = None
    best_stay = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        stay = 1 if (dx == 0 and dy == 0) else 0
        cand = (d, stay)
        if best_d is None or cand < (best_d, best_stay):
            best_d = d
            best_stay = stay
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]