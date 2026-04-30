def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def obs_pen(x, y):
        if not obstacles:
            return 0
        best = 10
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
                if best == 0:
                    break
        if best == 0:
            return 10**7
        if best == 1:
            return 50
        if best == 2:
            return 10
        if best == 3:
            return 3
        return 0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Choose best resource based on current advantage
    def best_adv(nx, ny):
        if not resources:
            return (-10**9, 10**9, 0)
        best_score = -10**18
        best_self = 10**9
        best_opp = 10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer/faster
            # prefer resources we can secure; also prefer shorter overall
            score = adv * 20 - sd - max(0, -adv) * 8
            if score > best_score:
                best_score = score
                best_self, best_opp = sd, od
        return (best_score, best_self, best_opp)

    best_move = (0, 0, -10**18)
    for dx, dy, nx, ny in moves:
        base, sd, od = best_adv(nx, ny)
        # If opponent is very close to our target, further bias to contest or dodge
        contest = 0
        if resources:
            contest = (od - sd) * 2
        # mild tendency to move away from opponent when no good advantage exists
        away = 0
        if contest <= 0:
            away = cheb(nx, ny, ox, oy) * 0.2
        # small preference for moving
        step = 0 if (dx == 0 and dy == 0) else 0.05
        score = base + away + contest + step - obs_pen(nx, ny)
        if score > best_move[2]:
            best_move = (dx, dy, score)

    return [int(best_move[0]), int(best_move[1])]