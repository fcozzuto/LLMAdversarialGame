def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obstacle_density(x, y):
        c = 0
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    if resources:
        nearest_to_self = min(resources, key=lambda p: (cheb(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        nearest_to_self = (ox, oy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Move potential: greedy toward resources + keep distance from opponent + avoid cramped/blocked cells
        if resources:
            d_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            d_opp = cheb(nx, ny, ox, oy)
            # If opponent is closer to a resource, slightly discourage giving them the edge by not over-approaching that resource
            d_opp_to_nearest = cheb(ox, oy, nearest_to_self[0], nearest_to_self[1])
            edge_penalty = 0
            if d_opp_to_nearest < d_self:
                edge_penalty = 2
            score = (-d_self * 3) + (d_opp * 1) - (obstacle_density(nx, ny) * 0.7) - edge_penalty
        else:
            score = cheb(nx, ny, ox, oy)  # just keep away if no resources visible

        # Deterministic tie-breaker by prefer smallest move index then lexicographic cell
        if score > best[0] or (score == best[0] and (nx, ny) < (best[1], best[2])):
            best = (score, nx, ny)

    tx, ty = best[1], best[2]
    return [tx - sx, ty - sy]