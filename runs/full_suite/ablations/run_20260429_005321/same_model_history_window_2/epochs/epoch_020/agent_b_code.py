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

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    neigh = dirs

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def obst_pen(x, y):
        pen = 0
        for dx, dy in neigh:
            if (x + dx, y + dy) in obst:
                pen += 2
        return pen

    best_move = [0, 0]
    best_sc = -10**18

    if not resources:
        # Minimal: move away from opponent a bit, avoid obstacles
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            d_opp = cheb(nx, ny, ox, oy)
            sc = d_opp - obst_pen(nx, ny)
            if sc > best_sc:
                best_sc = sc
                best_move = [dx, dy]
        return best_move

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        # Find resource where we gain most over opponent (self - opp), prefer closer overall.
        best_diff = -10**18
        best_dist = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(nx, ny, ox, oy, ) if False else None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            diff = do - ds  # positive => we are closer than opponent
            if diff > best_diff or (diff == best_diff and ds < best_dist):
                best_diff = diff
                best_dist = ds
        # Encourage moving toward a good target even if opponent is closer (still reduce ds).
        # Penalize getting near obstacles more than small distance gains.
        sc = best_diff * 100 - best_dist - obst_pen(nx, ny)
        # Small tie-breaker: prefer moves that increase distance from opponent when we aren't winning any resource yet.
        d_opp_now = cheb(nx, ny, ox, oy)
        sc += d_opp_now * 0.5 if best_diff <= 0 else 0.0
        if sc > best_sc:
            best_sc = sc
            best_move = [dx, dy]

    return best_move