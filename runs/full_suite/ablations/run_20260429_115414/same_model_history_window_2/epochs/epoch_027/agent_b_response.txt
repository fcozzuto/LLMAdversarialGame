def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    resources = observation.get("resources") or []
    rem = int(observation.get("remaining_resource_count", len(resources) if resources else 0))
    if not resources and rem > 0:
        resources = []

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def local_obst_pen(x, y):
        pen = 0
        for bx, by in blocked:
            if abs(bx - x) <= 1 and abs(by - y) <= 1:
                pen += 1
        return pen

    # If we know no resources, drift to a corner/center away from opponent
    if not resources:
        best = None
        for dx, dy, nx, ny in legal:
            # maximize distance from opponent, slight prefer toward center
            sc = cheb(nx, ny, ox, oy) - (abs(nx - (w-1)/2) + abs(ny - (h-1)/2))*0.01 - local_obst_pen(nx, ny)*0.1
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
        return [int(best[1]), int(best[2])]

    # Choose move that maximizes competitive advantage to a promising resource
    best = None
    for dx, dy, nx, ny in legal:
        obst = local_obst_pen(nx, ny)
        # Prefer resources where we are closer than opponent (positive advantage)
        best_target = -10**9
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # If opponent is already closer, still consider but with reduced value
            advantage = d_opp - d_self
            # Tie-break: prefer smaller self distance; and resource not "behind" obstacles locally (simple)
            cand = advantage * 2.0 - d_self * 0.15 - obst * 0.05
            if cand > best_target:
                best_target = cand
        # Also avoid stepping into squares that reduce our distance to the chosen resource too much
        sc = best_target - obst * 0.2
        # Deterministic tie-break: prefer larger dx then dy then staying near start->direction
        if best is None or sc > best[0] or (sc == best[0] and (dx > best[1] or (dx == best[1] and dy > best[2]))):
            best = (sc, dx, dy)
    return [int(best[1]), int(best[2])]