def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obstacles.add((px, py))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Prefer moving toward nearest resource, then toward center, while keeping away from opponent
    res_sorted = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if inb(rx, ry) and (rx, ry) not in obstacles:
            dist = cheb(rx, ry, sx, sy)
            res_sorted.append((dist, rx, ry))
    res_sorted.sort()

    center_x, center_y = w//2, h//2

    best = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        score = 0

        if res_sorted:
            nearest = res_sorted[0]
            nrx, nry = nearest[1], nearest[2]
            score -= cheb(nrx, nry, nx, ny) * 2

        dist_center = cheb(nx, ny, center_x, center_y)
        score -= dist_center

        # prefer staying away from opponent
        dist_opp = cheb(nx, ny, ox, oy)
        score += dist_opp

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]