def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    seen = set()
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in seen:
                seen.add((x, y))
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    best_r = None
    best_score = -10**18
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        margin = do - ds
        # Strongly prefer resources we can reach earlier than the opponent.
        score = margin * 120 - ds * 5
        # Avoid likely congestion with opponent row-sweep patterns.
        if ry == oy:
            score -= 18
        # Slight preference for forward movement away from opponent corner.
        score += (ds == 0) * 200
        # Prefer closer resources when margin ties.
        score -= abs(ry - (h - 1 - oy)) * 0.5
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    rx, ry = best_r
    best_next = (sx, sy)
    best_next_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy
        ds_next = dist((nx, ny), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        margin_next = do - ds_next
        ns = margin_next * 120 - ds_next * 5
        if ny == oy:
            ns -= 18
        # Keep it deterministic and stable: tie-break by preferring closer/then smaller delta.
        if ns > best_next_score:
            best_next_score = ns
            best_next = (nx, ny)

    nx, ny = best_next
    return [nx - sx, ny - sy]