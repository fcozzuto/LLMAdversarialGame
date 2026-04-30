def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    remaining = observation.get("remaining_resource_count", len(resources))

    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def neigh_cells(x, y):
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if ok(nx, ny):
                    yield (nx, ny)

    # If no resources or none remaining, move to center while keeping distance from opponent.
    if not resources or remaining <= 0:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = -dist((nx, ny), (cx, cy)) - 0.2 * dist((nx, ny), (ox, oy))
            if v > best[0] or (v == best[0] and (dx, dy) < (best[1], best[2])):
                best = (v, dx, dy)
        return [best[1], best[2]]

    opp_neighbors = set(neigh_cells(ox, oy))

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        my_d_opp = dist((nx, ny), (ox, oy))
        # Penalize moves that step into opponent's local pressure (adjacent)
        pressure_pen = 1.0 if (nx, ny) in opp_neighbors else 0.0

        # Consider best contested resource: we score by how much closer we are than opponent,
        # plus a small incentive to actually reduce our distance.
        score = -0.05 * my_d_opp
        for r in resources:
            rx, ry = r
            myd = dist((nx, ny), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            # Larger when we are closer than opponent; avoid giving opponent advantage.
            score += (opd - myd) - 0.02 * myd

        v = score - pressure_pen
        if v > best[0] or (v == best[0] and (dx, dy) < (best[1], best[2])):
            best = (v, dx, dy)

    return [best[1], best[2]]