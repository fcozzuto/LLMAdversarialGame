def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "pos" in r and isinstance(r.get("pos"), (list, tuple)) and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            elif "x" in r and "y" in r and r.get("x") is not None and r.get("y") is not None:
                resources.append((int(r["x"]), int(r["y"])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources or not inb(sx, sy):
        for dx, dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None  # (key1,key2,key3,tx,ty)
    for tx, ty in resources:
        if not inb(tx, ty):
            continue
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer winning resources (sd <= od-1), else best contest/closest
        win_margin = od - sd
        # Key: higher win_margin better; then smaller sd; then deterministic coordinate
        k1 = -win_margin
        k2 = sd
        k3 = (tx + ty, tx, ty)
        cand = (k1, k2, k3, tx, ty)
        if best is None or cand < best:
            best = cand
    _, _, _, tx, ty = best

    # Move one step: primary reduce distance to target; secondary increase distance from opponent
    curd = cheb(sx, sy, tx, ty)
    best_move = (10**9, -10**9, 10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        oppd = cheb(nx, ny, ox, oy)
        # Deterministic ordering via final tie on dx,dy
        score1 = nd - curd  # prefer negative
        score2 = oppd
        score3 = (abs(dx) + abs(dy), dx, dy)
        cand = (score1, -score2, score3, dx, dy)
        if cand < best_move:
            best_move = cand
    return [int(best_move[3]), int(best_move[4])]