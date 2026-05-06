def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 1))
    h = int(observation.get("grid_height", 1))
    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obst)
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
    target = (ox, oy)
    if resources and (observation.get("remaining_resource_count", None) is None or observation.get("remaining_resource_count", 1) > 0):
        best = None
        best_diff = -10**18
        for r in resources:
            d_our = man((sx, sy), r)
            d_opp = man((ox, oy), r)
            diff = d_opp - d_our
            if diff > best_diff:
                best_diff = diff
                best = r
        if best is not None:
            target = best
    tx, ty = target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        our_d = man((nx, ny), (tx, ty))
        opp_d = man((ox, oy), (tx, ty))
        val = (-our_d, opp_d)
        if val > (best_val, best_val):
            best_val = val[0]
            best_move = (dx, dy)
        elif val[0] == best_val:
            if (dx, dy) == (best_move[0], best_move[1]):
                pass
    if blocked(sx + best_move[0], sy + best_move[1]):
        for dx, dy in moves:
            if not blocked(sx + dx, sy + dy):
                return [int(dx), int(dy)]
    return [int(best_move[0]), int(best_move[1])]