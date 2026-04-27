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

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if resources:
        tar = min(resources, key=lambda p: (manh((mx,my), p), p[0], p[1]))
        tx, ty = tar
    else:
        tx, ty = (w-1) if abs(w-1-mx) >= 0 else w-1, (h-1) if abs(h-1-my) >= 0 else h-1
        # center fallback
        tx, ty = (w//2), (h//2)

    best_dx = 0
    best_dy = 0
    best_score = None

    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not safe(nx, ny):
            continue
        s = - (abs(nx - tx) + abs(ny - ty))
        # prioritize closer to target, then stay if same
        if best_score is None or s > best_score:
            best_score = s
            best_dx, best_dy = dx, dy

    # if no safe move toward target (blocked), try staying or a safe detour away from obstacle if possible
    if best_score is None:
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if safe(nx, ny):
                best_dx, best_dy = dx, dy
                break

    return [best_dx, best_dy]