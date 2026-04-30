def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # If no resources, drift to center while keeping distance from opponent.
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        best_sc = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            sc = -man(nx, ny, tx, ty) + 0.1 * man(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc, best = sc, (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    # Evaluate next-step cells: win/contend for nearest reachable resource.
    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        self_d_to_res = 10**9
        opp_d_to_res = 10**9
        on_res = 0
        # Choose resource that maximizes a "steal" advantage.
        steal_best = -10**18
        for rx, ry in resources:
            dS = man(nx, ny, rx, ry)
            dO = man(ox, oy, rx, ry)
            if dS < self_d_to_res: 
                self_d_to_res = dS
            if dO < opp_d_to_res:
                opp_d_to_res = dO
            # Advantage if we can get there sooner than opponent.
            # Encourage landing directly on a resource heavily.
            steal = 0
            if dS == 0:
                steal = 10**7
            else:
                steal = (dO - dS) * 200 - dS * 5
            if steal > steal_best:
                steal_best = steal
            if (nx, ny) == (rx, ry):
                on_res = 1

        # Also discourage moving into parity/close range that helps opponent capture.
        opp_near_after = min(man(nx, ny, rx, ry) - man(ox, oy, rx, ry) for rx, ry in resources)
        sc = steal_best + (on_res * 10**6) - man(nx, ny, ox, oy) * 1 + opp_near_after * 0.5
        # Deterministic tie-break: prefer smaller (dx,dy) in lexicographic order.
        if sc > best_sc or (sc == best_sc and (best is None or (dx, dy) < best)):
            best_sc, best = sc, (dx, dy)

    return [best[0], best[1]] if best else [0, 0]