def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    # Target selection: maximize opponent-self lead (advantage), tie-break by closer to us
    tx = ty = None
    if resources:
        best_adv = -10**9
        best_d = 10**9
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer
            if adv > best_adv or (adv == best_adv and sd < best_d) or (adv == best_adv and sd == best_d and (rx, ry) < (tx, ty) if tx is not None else True):
                best_adv = adv
                best_d = sd
                tx, ty = rx, ry
    else:
        tx, ty = W // 2, H // 2

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Main score: improve advantage at target; also keep away from opponent slightly
        ds = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        osd = cheb(ox, oy, tx, ty)
        adv_after = osd - ds
        score = adv_after * 1000 - ds * 5 - do  # deterministic linear heuristic
        # Prefer moves that approach target fastest on ties
        if score > best_score or (score == best_score and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]