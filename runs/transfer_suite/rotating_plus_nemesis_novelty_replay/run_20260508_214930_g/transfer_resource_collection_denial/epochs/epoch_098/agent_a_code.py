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
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        tx, ty = (w // 2, h // 2)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    my_half_right = sx > (w - 1) // 2
    if (ox > (w - 1) // 2) == my_half_right:
        my_half_right = not my_half_right

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Prefer the best resource on our half; if none, allow all.
        best_target = None
        best_my_dist = 10**9
        for (rx, ry) in resources:
            in_half = (rx > (w - 1) // 2) if my_half_right else (rx <= (w - 1) // 2)
            if not in_half:
                continue
            d = cheb((nx, ny), (rx, ry))
            if d < best_my_dist:
                best_my_dist = d
                best_target = (rx, ry)
        if best_target is None:
            for (rx, ry) in resources:
                d = cheb((nx, ny), (rx, ry))
                if d < best_my_dist:
                    best_my_dist = d
                    best_target = (rx, ry)

        rx, ry = best_target
        my_d = cheb((nx, ny), (rx, ry))
        opp_d = cheb((ox, oy), (rx, ry))
        # Maximize relative advantage; slight preference for moving toward opponent to contest row sweeps.
        score = (opp_d - my_d) * 1000 - my_d
        if dy != 0:
            score -= abs(ry - oy)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move