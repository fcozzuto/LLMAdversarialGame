def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, dict):
            pos = r.get("pos", None)
            if pos and len(pos) >= 2:
                resources.append((int(pos[0]), int(pos[1])))
            else:
                x, y = r.get("x", None), r.get("y", None)
                if x is not None and y is not None:
                    resources.append((int(x), int(y)))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [(dx, dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]

    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    # deterministically select target by combined proximity, biasing toward resources closer to our side
    # and away from opponent (estimate contest likelihood).
    best_target = resources[0]
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - myd, myd, rx, ry)  # prefer where we are relatively faster, then closer, then tie by coords
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d_to_t = cheb(nx, ny, tx, ty)

        # If stepping onto any resource, prioritize strongly (deterministic).
        on_res = 0
        for rx, ry in resources:
            if nx == rx and ny == ry:
                on_res = 1
                break

        # Repel opponent if they are closer (contest pressure).
        myd_new = cheb(nx, ny, tx, ty)
        od_new = cheb(ox, oy, tx, ty)
        opp_pressure = 1 if od_new <= myd_new else 0

        # tie-breaker by preferring moves that reduce distance to target, then increase distance from opponent.
        val = (on_res * 1000000) - d_to_t * 1000 + (cheb(nx, ny, ox, oy) * 10) - (opp_pressure * 200)

        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move