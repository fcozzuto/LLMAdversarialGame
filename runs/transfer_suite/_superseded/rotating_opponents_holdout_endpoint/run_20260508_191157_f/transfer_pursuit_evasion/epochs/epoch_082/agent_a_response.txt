def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obst = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("evader" not in self_role) and ("purs" in self_role or self_role == "")
    cxands = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def manh(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obst
    def edge_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)
    def mobility(x, y):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if legal(nx, ny):
                    cnt += 1
        return cnt
    target_corner = min(cxands, key=lambda c: manh(c[0], c[1], ox, oy)) if pursuer else max(cxands, key=lambda c: manh(c[0], c[1], ox, oy))
    best = (0, 0)
    bestv = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            dopp = manh(nx, ny, ox, oy)
            dmcorner = manh(nx, ny, target_corner[0], target_corner[1])
            # obstacle proximity penalty to avoid tight wall traps when evading
            near_obs = 0
            for (px, py) in obst:
                t = abs(nx - px) + abs(ny - py)
                if t <= 2:
                    near_obs += (3 - t)
            m = mobility(nx, ny)
            # Greedy pursuit vs escape with a wall-running twist (prefer moves with better mobility for evader)
            if pursuer:
                v = (-dopp * 10) + (-dmcorner) + (m * 0.5) + (-near_obs * 0.3)
            else:
                # maximize distance; also bias towards keeping open moves and towards the "farther" corner
                v = (dopp * 10) + (dmcorner) + (m * 1.2) + (edge_dist(nx, ny) * 0.6) + (-near_obs * 0.8)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
    return [int(best[0]), int(best[1])]