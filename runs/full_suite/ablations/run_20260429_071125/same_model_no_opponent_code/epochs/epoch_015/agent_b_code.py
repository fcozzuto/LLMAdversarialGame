def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def pos(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
            if "position" in v and isinstance(v["position"], (list, tuple)) and len(v["position"]) >= 2:
                return int(v["position"][0]), int(v["position"][1])
        return 0, 0

    sx, sy = pos(observation.get("self_position", [0, 0]))
    ox, oy = pos(observation.get("opponent_position", [0, 0]))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        q = pos(p)
        if 0 <= q[0] < w and 0 <= q[1] < h:
            obstacles.add(q)

    resources = []
    for p in observation.get("resources", []) or []:
        q = pos(p)
        if 0 <= q[0] < w and 0 <= q[1] < h and q not in obstacles:
            resources.append(q)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_t = resources[0]
        best_score = -10**18
        for rx, ry in resources:
            sd = dist2(sx, sy, rx, ry)
            od = dist2(ox, oy, rx, ry)
            # Prefer resources where we're closer; tie-break slightly toward lower total distance.
            score = (od - sd) * 1000 - (sd + od)
            if score > best_score:
                best_score = score
                best_t = (rx, ry)
        tx, ty = best_t

        best_move = (0, 0)
        best_mval = 10**30
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            mval = dist2(nx, ny, tx, ty)
            # If equally close, prefer staying away from opponent.
            if mval < best_mval:
                best_mval = mval
                best_move = (dx, dy)
            elif mval == best_mval:
                if dist2(nx, ny, ox, oy) > dist2(sx, sy, ox, oy):
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: move deterministically toward center while keeping distance from opponent.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_mval = 10**30
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        mval = dist2(nx, ny, cx, cy) - dist2(nx, ny, ox, oy)
        if mval < best_mval:
            best_mval = mval
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]