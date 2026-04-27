def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def manh(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # If resources exist, choose closest resource; else head toward opponent
    if resources:
        tx, ty = min(resources, key=lambda p: manh((mx, my), p))
    else:
        tx, ty = (ox, oy)

    best_dx = 0
    best_dy = 0
    best_score = None

    def score_move(dx, dy):
        nx, ny = mx + dx, my + dy
        if not safe(nx, ny):
            return None
        dist_to_t = abs(nx - tx) + abs(ny - ty)
        dist_to_o = abs(ox - nx) + abs(oy - ny)
        yours = -dist_to_t
        opp = -dist_to_o
        return (yours - opp, dist_to_t)

    for dx, dy in moves:
        res = score_move(dx, dy)
        if res is None:
            continue
        sc, dt = res
        if best_score is None or sc > best_score:
            best_score = sc
            best_dx, best_dy = dx, dy

    # Fallback to move toward target if no safe move found
    if best_score is None:
        dx = tx - mx
        dy = ty - my
        if dx != 0:
            dx = int(dx/abs(dx))
        else:
            dx = 0
        if dy != 0:
            dy = int(dy/abs(dy))
        else:
            dy = 0
        nx, ny = mx + dx, my + dy
        if safe(nx, ny):
            best_dx, best_dy = dx, dy
        else:
            best_dx, best_dy = 0, 0

    return [best_dx, best_dy]