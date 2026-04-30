def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cand_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if not resources:
            return -cheb(nx, ny, ox, oy)
        best = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # prefer grabbing/approaching resources where we can beat the opponent
            val = (do - ds) * 10 - ds
            # small bonus if we are at/near a resource (likely immediate pickup)
            if ds == 0:
                val += 200
            elif ds == 1:
                val += 40
            best = val if val > best else best
        # also avoid walking into positions that give opponent a clear tempo
        dist_adv = cheb(nx, ny, ox, oy)
        best += max(0, 4 - dist_adv) * 2
        return best

    best_move = (0, 0)
    best_val = cand_score(sx, sy)
    # deterministic tie-breaking: choose smallest dx,dy by fixed dir order (already deterministic)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = cand_score(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]