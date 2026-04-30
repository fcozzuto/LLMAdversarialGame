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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            my_d = cheb(sx, sy, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            key = (op_d - my_d, -my_d, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
        best_move = (0, 0)
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            my_d = cheb(nx, ny, tx, ty)
            op_d = cheb(ox, oy, tx, ty)
            score = (op_d - my_d, -my_d, dx, dy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        # No visible resources: drift toward center while avoiding opponent a bit
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move = (0, 0)
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist_center = cheb(nx, ny, cx, cy)
            dist_opp = cheb(nx, ny, ox, oy)
            score = (dist_opp, -dist_center, -abs(dx)-abs(dy))
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]