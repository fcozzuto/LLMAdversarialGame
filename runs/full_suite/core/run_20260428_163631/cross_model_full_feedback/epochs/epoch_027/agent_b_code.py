def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obst.add((px, py))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obst:
                resources.append((rx, ry))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    remaining = int(observation.get("remaining_resource_count", len(resources)) or len(resources))

    if resources:
        # Target nearest resource with tie-break by distance to opponent
        best = None
        best_score = None
        for rx, ry in resources:
            dist_me = max(abs(rx - sx), abs(ry - sy))
            dist_op = max(abs(rx - ox), abs(ry - oy))
            score = (dist_me, dist_op)
            if best is None or score < best_score:
                best = (rx, ry)
                best_score = score
        tx, ty = best
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if (sx+dx, sy+dy) not in obst:
            return [dx, dy]
        # fallback toward resource
        return [dx if dx != 0 else 0, dy if dy != 0 else 0]

    # No visible resources: move toward opponent if safe, else stay or step away
    dx = 0
    dy = 0
    if ox != sx:
        dx = 1 if ox > sx else -1
    if oy != sy:
        dy = 1 if oy > sy else -1

    # try prefer not stepping into obstacle or out of bounds
    cand = (sx+dx, sy+dy)
    if inb(*cand) and cand not in obst:
        return [dx, dy]

    # try other adjacent safe moves
    for adx, ady in legal:
        if (sx+adx, sy+ady) not in obst:
            return [adx, ady]

    return [0, 0]