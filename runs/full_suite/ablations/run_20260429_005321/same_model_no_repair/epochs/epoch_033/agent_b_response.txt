def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    obs = set((x, y) for x, y in obstacles)

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def valid(nx, ny): return inb(nx, ny) and (nx, ny) not in obs

    if not resources:
        best = (None, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            d = man(nx, ny, ox, oy)
            if best[0] is None or d > best[1]:
                best = (1, d, dx if dx else 0)  # deterministic tie stub
        # deterministic tie-break towards staying
        for dx, dy in [(0, 0)] + [m for m in moves if m != (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny): return [dx, dy]
        return [0, 0]

    def best_target_metric(px, py, qx, qy, inv=False):
        # if inv=False: we want (their next advantage - our distance)
        # if inv=True: for opponent perspective
        best = None
        for rx, ry in resources:
            ds = man(px, py, rx, ry)
            do = man(qx, qy, rx, ry)
            metric = (do - ds) if not inv else (ds - do)
            if best is None or metric > best[0] or (metric == best[0] and (ds < best[1] or (ds == best[1] and (rx, ry) < best[2]))):
                best = (metric, ds, (rx, ry))
        return best[2]

    def opp_greedy_move(px_our, py_our):
        # predict opponent move by their greedy target choice after moving
        best_move = (0, 0)
        best_val = None
        for dx, dy in moves:
            nxo, nyo = ox + dx, oy + dy
            if not valid(nxo, nyo): continue
            # opponent picks target that maximizes their advantage metric against us
            tx, ty = best_target_metric(nxo, nyo, px_our, py_our, inv=True)
            ourd = man(px_our