def choose_move(observation):
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0
    if w <= 0 or h <= 0:
        return [0, 0]
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # Strategic shift: prioritize resources where we gain relative tempo vs opponent,
    # and slightly avoid moving into opponent proximity.
    best = None
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        opp_dist_next = cheb(nx, ny, ox, oy)
        # proximity penalty grows sharply when very close
        prox_pen = 0
        if opp_dist_next <= 1:
            prox_pen = 2.5
        elif opp_dist_next <= 2:
            prox_pen = 1.0
        elif opp_dist_next <= 3:
            prox_pen = 0.4

        if resources:
            # choose best resource by relative advantage (op farther than us)
            best_res_val = -10**18
            for rx, ry in resources:
                my = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # maximize: (opd - my) = how much we are ahead in tempo
                # plus small preference for decreasing my distance to finish sooner
                v = (opd - my) * 1.2 - my * 0.08
                # slight tie-break toward center-ish (reduces wall-hugging stalling)
                cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
                v -= (abs(nx - cx) + abs(ny - cy)) * 0.01
                if v > best_res_val:
                    best_res_val = v
            val = best_res_val - prox_pen
        else:
            # no resources: move away from opponent a bit deterministically
            val = opp_dist_next - prox_pen - (nx + ny) * 0.0001

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]