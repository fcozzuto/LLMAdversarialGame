def choose_move(observation):
    def to_xy(v):
        if not v or len(v) < 2:
            return (0, 0)
        return (int(v[0]), int(v[1]))

    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = to_xy(observation.get("self_position"))
    ox, oy = to_xy(observation.get("opponent_position"))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            cell = (int(r[0]), int(r[1]))
            if cell not in obstacles:
                resources.append(cell)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        best = (-(10**9), 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist_cheb(nx, ny, ox, oy)
            if d > best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Pick resource where we have the biggest "lead" over opponent (tie-break by closer to us).
    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = dist_cheb(sx, sy, rx, ry)
        do = dist_cheb(ox, oy, rx, ry)
        lead = do - ds
        key = (lead, -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    # Move greedily toward chosen resource; avoid obstacles; if multiple, pick deterministic tie.
    best = (-(10**9), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist_cheb(nx, ny, rx, ry)
        # Slightly prefer increasing distance from opponent if equal.
        opp_d = dist_cheb(nx, ny, ox, oy)
        score = (-d, opp_d)
        if score > best[0:2] or best[0] < -10**8:
            best = (score[0], dx, dy) if score[0] != best[0] else ((score[0], score[1], dx, dy), dx, dy)

    # The above can create odd structure; redo cleanly with deterministic selection.
    best_s = None
    best_dx, best_dy = 0, 0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist_cheb(nx, ny, rx, ry)
        opp_d = dist_cheb(nx, ny, ox, oy)
        key = (d, -opp_d, dx, dy)
        if best_s is None or key < best_s:
            best_s = key
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]