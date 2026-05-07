def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    moves = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best_r = None
    best_tiebreak = -10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer or at least not worse; tie-break by maximizing (do-ds)
        takeover = (do - ds)
        # Also slightly prefer cells closer overall to reduce idle time
        val = 1000 * takeover - ds
        if val > best_tiebreak:
            best_tiebreak = val
            best_r = (rx, ry)

    rx, ry = best_r
    # If we're already on a resource, don't waste a move
    if (sx, sy) == (rx, ry):
        return [0, 0]

    # Choose the move that most reduces distance to target, with obstacle constraint and small anti-opponent term
    best = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, rx, ry)
        no = cheb(ox, oy, rx, ry)
        takeover_after = (no - ns)
        score = 1000 * takeover_after - ns
        # minor preference to keep away from opponent when score equal
        score += -0.01 * cheb(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]