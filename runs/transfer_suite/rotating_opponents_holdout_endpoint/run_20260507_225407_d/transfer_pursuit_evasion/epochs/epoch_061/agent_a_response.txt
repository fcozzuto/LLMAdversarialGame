def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("evasion" in r) or ("avoid" in r)

    self_role = observation.get("self_role", "") or ""
    if not is_evader(self_role) and is_evader(observation.get("self_role_name", "")) :
        self_role = observation.get("self_role_name", "")
    if not is_evader(self_role) and is_evader(observation.get("role", "")) :
        self_role = observation.get("role", "")
    self_is_evader = is_evader(self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs8 = moves
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner_order = sorted(corners, key=lambda c: (-(c[0] != ox) - (c[1] != oy), (c[0]-ox)**2 + (c[1]-oy)**2))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    tx, ty = None, None
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if nx == ox and ny == oy:
            sc = 10**9 if not self_is_evader else -10**9
        else:
            free = 0
            for ddx, ddy in dirs8:
                ax, ay = nx + ddx, ny + ddy
                if valid(ax, ay):
                    free += 1
            obst_near = 8 - free
            if self_is_evader:
                # Flee, but avoid dead-ends and prefer farthest open corner.
                target_corner = None
                for c in corner_order:
                    if valid(c[0], c[1]):
                        target_corner = c
                        break
                tcx, tcy = target_corner if target_corner else (0, 0)
                corner_d2 = (nx - tcx) * (nx - tcx) + (ny - tcy) * (ny - tcy)
                sc = d2 + 0.35 * corner_d2 - 0.6 * obst_near
            else:
                # Pursue, avoid obstacles and prefer moves that squeeze.
                sc = -d2 - 0.3 * obst_near
            # Tie-break deterministically: prefer lexicographically smaller move delta.
        cand = (sc, -abs(dx) - abs(dy), -free)
        if best is None or cand > best[0] or (cand == best[0] and (dx, dy) < best[1]):
            best = (cand, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]