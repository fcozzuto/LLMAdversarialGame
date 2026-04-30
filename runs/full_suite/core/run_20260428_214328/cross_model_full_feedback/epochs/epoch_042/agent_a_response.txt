def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # No resources visible: move to maximize distance from opponent (avoid fights)
        best = None; bestv = None
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, ox, oy)
            if bestv is None or v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Competition-aware target: my distance minus advantage if opponent is farther too.
    best = None; bestv = None
    for dx, dy, nx, ny in legal:
        # Prefer moves that reduce distance to some resource where I can beat opponent.
        best_target = None; best_target_val = None
        for rx, ry in resources:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Lower is better: prioritize close resources and winning contests (dm - do).
            val = dm - 0.85 * do
            # Tie-break: prefer resources closer to me when contest strength equal.
            if best_target_val is None or val < best_target_val or (val == best_target_val and dm < best_target_val2):
                best_target_val = val
                best_target_val2 = dm
                best_target = (rx, ry)
        # Secondary: keep away from opponent a bit to avoid blocking/stealing next.
        v = best_target_val - 0.10 * cheb(nx, ny, ox, oy)
        if bestv is None or v < bestv:
            bestv = v; best = (dx, dy)

    return [int(best[0]), int(best[1])]