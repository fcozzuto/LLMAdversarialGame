def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def near_obstacle(x, y):
        m = 999
        for dx in (-1, 0, 1):
            nx = x + dx
            if nx < 0 or nx >= w: 
                continue
            for dy in (-1, 0, 1):
                ny = y + dy
                if (nx, ny) in obstacles:
                    m = 0
        return m

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy

        # Choose a target resource by maximizing my advantage after this move
        move_score = 0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Prefer resources I can reach sooner; strongly prefer uncontested (opd > myd)
            adv = (opd - myd)
            s = 0
            if myd == 0:
                s += 10_000_000
            # Uncontested/contestable shaping
            if adv > 0:
                s += 300_000 * adv + 50_000 // (1 + myd)
            elif adv == 0:
                s += 25_000 // (1 + myd)
            else:
                s += adv * 10  # penalty when opponent is closer

            # Obstacle pressure avoidance: mild penalty if stepping adjacent to obstacles
            s -= 2000 * (near_obstacle(nx, ny) == 0)

            if s > move_score:
                move_score = s

        # Small tie-break: keep moving toward overall closest "best" resource
        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]