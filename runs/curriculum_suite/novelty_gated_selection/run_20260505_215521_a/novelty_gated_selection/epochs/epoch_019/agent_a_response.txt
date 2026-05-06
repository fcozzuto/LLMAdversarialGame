def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy
    def step_toward(px, py, tx, ty):
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            d = man(nx, ny, tx, ty)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best[0] < 10**9 else [0, 0]
    def eval_from(nsx, nsy):
        if not resources:
            # drift: minimize distance from center while keeping away from obstacles is implicit via validity
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            best = (-10**18, 0, 0)
            for dx, dy in moves:
                tx, ty = nsx + dx, nsy + dy
                if not inb(tx, ty) or (tx, ty) in obst:
                    continue
                v = -(abs(tx - cx) + abs(ty - cy))
                if v > best[0]:
                    best = (v, dx, dy)
            return [best[1], best[2]]
        # anticipate opponent greedily targeting the same resource we would pursue
        bestv, bestdx, bestdy = -10**18, 0, 0
        for dx, dy in moves:
            tx, ty = nsx + dx, nsy + dy
            if not inb(tx, ty) or (tx, ty) in obst:
                continue
            # choose the resource that gives maximal expected advantage
            best_adv = -10**18
            for rx, ry in resources:
                d_self = man(tx, ty, rx, ry)
                odx, ody = step_toward(ox, oy, rx, ry)
                nox, noy = ox + odx, oy + ody
                d_opp = man(nox, noy, rx, ry)
                # If we can get closer than opponent after one step, prefer it; also encourage faster overall
                urg = 0
                if rx == 0 or rx == w - 1 or ry == 0 or ry == h - 1:
                    urg = 1
                adv = (d_opp - d_self) * 3 + urg * (d_opp - d_self) - 0.2 * d_self
                if adv > best_adv:
                    best_adv = adv
            # slight tie-break: avoid getting stuck near obstacles (implicitly via moves) and prefer lower own distance
            if best_adv > bestv:
                bestv, bestdx, bestdy = best_adv, dx, dy
        return [bestdx, bestdy]
    # main choose: evaluate our moves from current
    return eval_from(sx, sy)