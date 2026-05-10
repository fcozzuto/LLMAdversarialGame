def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev: shortest with 8-way moves

    valid = []
    for r in resources:
        rx, ry = r[0], r[1]
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            valid.append((rx, ry))
    if not valid:
        # No reachable resources: try to reduce opponent's access by moving toward center-ish
        cx, cy = w // 2, h // 2
        best = [0, 0]
        bestv = -10**9
        for dx, dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            v = dist(nx, ny, cx, cy) - dist(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    tr = observation.get("turns_remaining", 0)
    few = (observation.get("remaining_resource_count", len(valid)) <= 3) or (tr <= 6)

    # Pick best target deterministically
    best_target = None
    best_val = -10**18
    for rx, ry in valid:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Primary: win contests (opp farther than us). Secondary: quick pickup.
        margin = od - sd  # positive means we get there earlier
        val = margin * 100.0 - sd * (5.0 if not few else 9.0)
        if sd == 0:
            val += 10000.0
        # Tie-break: prefer upper-left to remain deterministic
        val += (-rx - ry) * 0.001
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target

    # Choose step toward target, but avoid obstacles; if blocked, try alternate steps
    candidates = [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    best_move = [0, 0]
    best_move_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        nsd = dist(nx, ny, tx, ty)
        nod = dist(nx, ny, ox, oy)
        # Encourage increasing winning margin for the chosen target; otherwise keep it safe
        mv = (dist(ox, oy, tx, ty) - nsd) * 100.0 - nsd * (6.0 if not few else 10.0) - nod * 0.05
        # Slight preference for moving closer to target and staying deterministic
        mv += (-(abs(nx - tx) + abs(ny - ty))) * 0.001 - (nx * 0.000001 + ny * 0.0000001)
        if mv > best_move_val:
            best_move_val = mv
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]