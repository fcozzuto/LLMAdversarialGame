def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                if (x, y) not in obst:
                    res.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_score = None

    # Simple deterministic priority:
    # 1) If resource available and not occupied, move towards nearest resource.
    # 2) Else move to increase distance from opponent while staying safe.
    def dist_to_resource(x, y):
        if not res:
            return 10**9
        d = min(cheb(x, y, rx, ry) for rx, ry in res)
        return d

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        # If moving into opponent's cell, disallow
        if nx == ox and ny == oy:
            continue
        d_res = dist_to_resource(nx, ny)
        d_opp = cheb(nx, ny, ox, oy)
        score = (0 if d_res == 10**9 else (100 - d_res)) * 1000  # prioritize nearer resource
        # prefer keeping distance from opponent
        score += (d_opp * -1)

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        # If no safe move, stay
        return [0, 0]

    return [int(best[0]), int(best[1])]