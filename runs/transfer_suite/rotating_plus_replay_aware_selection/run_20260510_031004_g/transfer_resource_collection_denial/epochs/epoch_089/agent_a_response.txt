def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Choose a target maximizing (opp arrives later) and favoring closer own arrival.
    best_r = resources[0]
    best_key = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        key = (opp_d - my_d, -my_d, -abs(rx - sx) - abs(ry - sy), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Evaluate possible moves: avoid obstacles, and maximize immediate advantage toward the target.
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        my_d2 = cheb(nx, ny, rx, ry)
        opp_d2 = cheb(ox, oy, rx, ry)
        # Prefer moves that increase advantage and reduce distance; tie-break deterministically.
        score = (opp_d2 - my_d2, -my_d2, -abs(nx - rx) - abs(ny - ry), -dx, -dy, nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move