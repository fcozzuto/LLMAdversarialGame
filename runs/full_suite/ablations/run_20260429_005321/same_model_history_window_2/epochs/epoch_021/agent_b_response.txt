def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_adj_pen(x, y):
        pen = 0
        for dx, dy in neigh:
            if (x + dx, y + dy) in obst:
                pen += 1
        return pen

    def best_target_value(px, py):
        best = -10**18
        for rx, ry in resources:
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner than opponent; also prefer closeness to reduce travel
            val = (do - ds) * 10 - ds
            # Avoid resources that are likely boxed by obstacles near our next step
            val -= obst_adj_pen(px, py) * 1.5
            if val > best: best = val
        return best if best != -10**18 else 0

    best_move = (0, 0)
    best_score = -10**18

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): continue
            if (nx, ny) in obst:
                continue
            score = best_target_value(nx, ny)
            # Small tie-break: move generally away from opponent if tied
            score += (cheb(nx, ny, ox, oy) * 0.02)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # No visible resources: maximize distance from opponent while avoiding obstacles
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): continue
            if (nx, ny) in obst: continue
            score = cheb(nx, ny, ox, oy) * 10 - obst_adj_pen(nx, ny) * 2
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]