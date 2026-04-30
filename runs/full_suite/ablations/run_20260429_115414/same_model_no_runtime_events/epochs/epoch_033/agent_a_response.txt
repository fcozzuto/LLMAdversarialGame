def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    rem = int(observation.get("remaining_resource_count") or len(resources))
    if not resources:
        return [0, 0]

    def cheb(a, b, x, y):
        dx = a - x
        if dx < 0: dx = -dx
        dy = b - y
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obs_pen(x, y):
        if not obstacles:
            return 0
        p = 0
        for ox1, oy1 in obstacles:
            if cheb(ox1, oy1, x, y) <= 1:
                p += 3
                if (x, y) == (ox1, oy1):
                    p += 10
        return p

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    late = rem <= 5

    best_move = [0, 0]
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        best_adv = -10**9
        best_closeness = 10**9
        for rx, ry in resources:
            d_self = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            d_next = cheb(nx, ny, rx, ry)
            adv = d_opp - d_next
            if adv > best_adv:
                best_adv = adv
            if d_next < best_closeness:
                best_closeness = d_next
        # Objective: take resources you are closer to; late game: pure closeness.
        val = (best_adv * 10) - obs_pen(nx, ny)
        if late:
            val += max(0, 8 - best_closeness) * 5
        else:
            val += max(0, 8 - best_closeness)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move