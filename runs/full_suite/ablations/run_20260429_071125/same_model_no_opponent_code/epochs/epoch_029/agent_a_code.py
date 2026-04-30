def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    occ = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                occ.add((px, py))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in occ:
                resources.append((rx, ry))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def safe(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in occ

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def adj_block(nx, ny):
        cnt = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            tx, ty = nx + dx, ny + dy
            if (tx, ty) in occ:
                cnt += 1
        return cnt

    def eval_move(nx, ny):
        if resources:
            best = 10**9
            for rx, ry in resources:
                myd = md(nx, ny, rx, ry)
                opd = md(ox, oy, rx, ry)
                # prefer resources we're closer to than opponent
                score = myd - 0.6 * opd
                # encourage grabbing closer resources
                score += 0.15 * myd * myd / 10.0
                if score < best:
                    best = score
            # avoid moving too close to opponent unless also advantageous by resources
            opp_close = md(nx, ny, ox, oy)
            best += 0.35 * max(0, 8 - opp_close)
            # slight penalty for hugging obstacles
            best += 0.2 * adj_block(nx, ny)
            return best
        # no resources: head to center and slightly away from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = abs(nx - cx) + abs(ny - cy)
        away = -md(nx, ny, ox, oy)
        return 1.0 * center + 0.05 * away

    best_move = (0, 0)
    best_val = 10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not safe(nx, ny):
            continue
        v = eval_move(nx, ny)
        if v < best_val - 1e-12:
            best_val = v
            best_move = (dx, dy)
        elif abs(v - best_val) <= 1e-12:
            # deterministic tie-break: prefer moves with smaller (dx,dy) lexicographically
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]