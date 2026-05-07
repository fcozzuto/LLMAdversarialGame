def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    if not (isinstance(sx, int) and isinstance(sy, int) and 0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                oset.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_to(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in oset:
            return [dx, dy]
        # try axis alternatives deterministically
        if dx != 0:
            ax, ay = sx + dx, sy
            if inb(ax, ay) and (ax, ay) not in oset:
                return [dx, 0]
        if dy != 0:
            ax, ay = sx, sy + dy
            if inb(ax, ay) and (ax, ay) not in oset:
                return [0, dy]
        return [0, 0]

    if resources:
        # candidate next moves: all 9 deltas
        deltas = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                deltas.append((dx, dy))
        best = None
        best2 = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in oset:
                continue
            # deny/progress heuristic: maximize (opp_dist - self_dist) for the best resource for us
            best_diff = -10**9
            best_our_dist = 10**9
            for rx, ry in resources:
                d_s = abs(nx - rx) + abs(ny - ry)
                d_o = abs(ox - rx) + abs(oy - ry)
                diff = d_o - d_s
                if diff > best_diff or (diff == best_diff and d_s < best_our_dist):
                    best_diff = diff
                    best_our_dist = d_s
            # secondary tie-break: prefer moves that reduce nearest resource distance
            nearest = best_our_dist
            score = best_diff * 1000 - nearest
            if best is None or score > best:
                best = score
                best2 = (dx, dy)
        if best2 is not None:
            return [int(best2[0]), int(best2[1])]

    # fallback: head toward a deterministic corner (opponent can't be stopped forever; keep movement valid)
    target = (w - 1, h - 1) if (sx + sy) <= (w - 1 - sx + h - 1 - sy) else (0, h - 1)
    return step_to(target[0], target[1])