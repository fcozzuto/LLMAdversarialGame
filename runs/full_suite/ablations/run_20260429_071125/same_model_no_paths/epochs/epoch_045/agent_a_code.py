def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = (0, 0)
    best_val = -10**18

    if not ok(sx, sy):
        for dx, dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    opp_threat = cheb(sx, sy, ox, oy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            d_me = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            d_opp = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
            # Greedy to nearest resource; also prefer moves that keep opponent at a disadvantage
            val = -(d_me * 100)
            val += (opp_threat - cheb(nx, ny, ox, oy)) * 3
            val += (d_opp - cheb(nx, ny, ox, oy)) * 0.5
            # If landing closer to a specific resource, slight preference for diagonal/forward progress
            val += (abs(nx - ox) + abs(ny - oy)) * 0.01
        else:
            val = -(cheb(nx, ny, ox, oy)) * 1
        # Deterministic tie-break: prefer lexicographically smaller move deltas
        cand = (val, -dx, -dy)
        if cand[0] > best_val or (cand[0] == best_val and (dx, dy) < best):
            best_val = cand[0]
            best = (dx, dy)

    return [int(best[0]), int(best[1])]