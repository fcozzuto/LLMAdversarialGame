def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
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

    if not resources:
        dx = 0
        dy = 0
        if sx < ox: dx = 1
        elif sx > ox: dx = -1
        elif sy < oy: dy = 1
        elif sy > oy: dy = -1
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        if (sx, sy) not in obstacles:
            return [0, 0]
        for ddx, ddy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1), (0, 0)]:
            nx, ny = sx + ddx, sy + ddy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [ddx, ddy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    best = [0, 0]
    best_s = -10**18
    bias_x = 1 if (ox + oy) >= ((w - 1 - ox) + (h - 1 - oy)) else 0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        dist_to_nearest = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        dist_to_opp = cheb(nx, ny, ox, oy)
        forward = (nx - sx) if bias_x else (ny - sy)
        s = -dist_to_nearest * 10 + dist_to_opp - (0 if forward >= 0 else 1)
        if forward < 0:
            s -= 0.5
        if s > best_s:
            best_s = s
            best = [dx, dy]

    return best