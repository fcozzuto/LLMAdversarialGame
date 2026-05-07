def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    sx = max(0, min(w - 1, int(sx)))
    sy = max(0, min(h - 1, int(sy)))
    ox = max(0, min(w - 1, int(ox)))
    oy = max(0, min(h - 1, int(oy)))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If resources exist, pick move that maximizes advantage: (opp_dist - self_dist) to the same resource.
    if resources:
        best_move = (0, 0)
        best_val = None
        rlist = []
        for r in resources:
            try:
                tx, ty = int(r[0]), int(r[1])
            except:
                continue
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                rlist.append((tx, ty))
        if rlist:
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not valid(nx, ny):
                    continue
                # Tie-break deterministically: prefer smaller (nx,ny) if values equal.
                best_for_move = None
                for tx, ty in rlist:
                    sd = cheb(nx, ny, tx, ty)
                    od = cheb(ox, oy, tx, ty)
                    # prefer taking resources where we can be closer than opponent; also slightly prefer smaller own distance.
                    val = (od - sd) * 100 - sd
                    if best_for_move is None or val > best_for_move:
                        best_for_move = val
                if best_for_move is None:
                    best_for_move = -cheb(nx, ny, w//2, h//2)
                if best_val is None or best_for_move > best_val or (best_for_move == best_val and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
                    best_val = best_for_move
                    best_move = (dx, dy)
            return [int(best_move[0]), int(best_move[1])]

    # Fallback: head toward center-ish (deterministic).
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = (0, 0)
    bestd = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, cx, cy)
        if bestd is None or d < bestd or (d == bestd and (nx, ny) < (sx + best[0], sy + best[1])):
            bestd = d
            best = (dx, dy)
    return [int(best[0]), int(best[1])]