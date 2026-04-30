def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_dx, best_dy = 0, 0

    if resources:
        # Move toward closest resource while avoiding opponent and obstacles
        best_score = None
        for rx, ry in resources:
            dme = cheb(sx, sy, rx, ry)
            dod = cheb(ox, oy, rx, ry)
            # heuristic: prioritize reducing distance to resource, but stay away from opponent
            score = -dme * 2 - dod
            # choose a neighboring cell that decreases distance to resource
            cand = []
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = sx + dx, sy + dy
                    if not legal(nx, ny):
                        continue
                    nd = cheb(nx, ny, rx, ry)
                    delta = dme - nd
                    o_dist = cheb(nx, ny, ox, oy)
                    score2 = delta * 3 - o_dist
                    cand.append((score2, dx, dy))
            if cand:
                cand.sort(reverse=True)
                sc, dx, dy = cand[0]
                if best_score is None or sc > best_score:
                    best_score = sc
                    best_dx, best_dy = dx, dy
        # final safety: ensure move is legal (engine will handle otherwise)
        if not legal(sx + best_dx, sy + best_dy):
            best_dx, best_dy = 0, 0
        return [best_dx, best_dy]
    else:
        # No resources: head toward center to optimize future captures, but avoid opponent
        tx, ty = w // 2, h // 2
        best_dx, best_dy = 0, 0
        best_score = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not legal(nx, ny):
                    continue
                d = cheb(nx, ny, tx, ty)
                o = cheb(nx, ny, ox, oy)
                sc = -d * 2 - o
                if best_score is None or sc > best_score:
                    best_score = sc
                    best_dx, best_dy = dx, dy
        if not legal(sx + best_dx, sy + best_dy):
            best_dx, best_dy = 0, 0
        return [best_dx, best_dy]