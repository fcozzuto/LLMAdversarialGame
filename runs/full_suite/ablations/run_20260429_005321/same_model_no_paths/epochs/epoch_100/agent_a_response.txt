def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]); op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1]); ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles
    def best_target_dist(ax, ay):
        if resources:
            best = None
            for rx, ry in resources:
                myd = cheb(ax, ay, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                diff = opd - myd
                val = (diff, -myd)  # maximize diff, then closer
                if best is None or val > best[0]:
                    best = (val, myd)
            return best[1] if best else 0
        return cheb(ax, ay, (w - 1) // 2, (h - 1) // 2)
    # If resources exist, move to maximize advantage vs opponent for contested resources.
    best_move = (None, (-10**9, 10**9, 0))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy
        if resources:
            # Evaluate this move by the best resource advantage it enables.
            best_diff = -10**9; best_myd = 10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                diff = opd - myd
                if diff > best_diff or (diff == best_diff and myd < best_myd):
                    best_diff, best_myd = diff, myd
            # Small tie-breaker: prefer reducing distance to center when diff is similar.
            center_d = cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
            val = (best_diff, -best_myd, -center_d)
        else:
            # No resources visible: go toward center deterministically.
            d = best_target_dist(nx, ny)
            val = (-d, 0, 0)
        if val > best_move[1]:
            best_move = ((dx, dy), val)
    dx, dy = best_move[0]
    return [int(dx), int(dy)]