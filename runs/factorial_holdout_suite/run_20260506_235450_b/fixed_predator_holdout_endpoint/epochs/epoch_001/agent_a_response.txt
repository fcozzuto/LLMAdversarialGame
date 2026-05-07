def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        # No visible resources: drift toward center while avoiding obstacles/opponent slightly
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources I'm closer to; if tie, prefer higher "recent" not available -> deterministic by coordinates
            key = (ds - do, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    def valid(nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return False
        if (nx, ny) in obstacles:
            return False
        return True

    cands = []
    # Candidate deltas include staying still
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dcur = man(nx, ny, tx, ty)
            dp = man(nx, ny, ox, oy)
            # Goal: reduce distance to target; if opponent very close, avoid moving into them
            opp_pen = 0
            if dp == 0:
                opp_pen = 100
            elif dp == 1:
                opp_pen = 25
            elif dp == 2:
                opp_pen = 8
            cands.append((dcur + opp_pen, dp, dx, dy, nx, ny))
    if not cands:
        return [0, 0]

    cands.sort()
    _, _, dx, dy, nx, ny = cands[0]

    # If can't get closer due to obstacle traps, try immediate alternative that reduces resource distance most.
    # Deterministic: choose best among moves that are strictly closer; otherwise keep best.
    curd = man(sx, sy, tx, ty)
    closer = [c for c in cands if man(c[4], c[5], tx, ty) < curd]
    if closer:
        closer.sort()
        return [closer[0][2], closer[0][3]]
    return [dx, dy]