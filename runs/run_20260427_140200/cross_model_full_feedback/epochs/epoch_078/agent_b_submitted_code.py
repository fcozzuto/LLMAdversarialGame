def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is None: 
            continue
        if len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is None:
            continue
        if len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def dist_cheb(a, b, c):
        da = abs(a - c[0])
        db = abs(b - c[1])
        return max(da, db)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    if resources:
        best_target = None
        best_score = None
        for rx, ry in resources:
            d_me = max(abs(mx - rx), abs(my - ry))
            d_opp = max(abs(ox - rx), abs(oy - ry))
            score = -d_me  - max(0, d_opp - 1)
            if best_score is None or score > best_score:
                best_score = score
                best_target = (rx, ry)
        if best_target:
            tx, ty = best_target
            best = None
            mdx = tx - mx
            mdy = ty - my
            step_x = 0 if mdx == 0 else (1 if mdx > 0 else -1)
            step_y = 0 if mdy == 0 else (1 if mdy > 0 else -1)
            if legal(mx + step_x, my + step_y):
                best = [step_x, step_y]
            else:
                for dx, dy in moves:
                    nx, ny = mx + dx, my + dy
                    if legal(nx, ny):
                        best = [dx, dy]
                        break

    if best is not None:
        return best

    # Fallback: move away from opponent if possible
    dx = 0
    dy = 0
    if ox > mx:
        dx = -1
    elif ox < mx:
        dx = 1
    if oy > my:
        dy = -1
    elif oy < my:
        dy = 1
    if legal(mx + dx, my + dy):
        return [dx, dy]

    # Try to stay put if safe
    if legal(mx, my):
        return [0, 0]

    # Last resort: any legal move
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if legal(nx, ny):
            return [dx, dy]

    return [0, 0]