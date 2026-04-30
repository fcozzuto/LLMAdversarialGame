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
    chase_weight = 3.0 if remaining <= 6 else 1.6
    block_weight = 1.8 if remaining <= 6 else 1.0

    best_move = legal[0]
    best_val = -10**9

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dist_res = 999
        for rx, ry in resources:
            d = max(abs(rx - nx), abs(ry - ny))
            if d < dist_res:
                dist_res = d
        if resources:
            val = -dist_res * 2
            # encourage moving toward resource
            val += -(abs(nx - ox) + abs(ny - oy))  # slight deterrent from opponent
            # add proximity to resource
            if dist_res == 0:
                val += 50
        else:
            val = -abs(nx - ox) - abs(ny - oy)

        # simple obstacle penalty to avoid getting cornered
        if (nx, ny) in obst:
            val -= 5

        # keep some bias toward center
        cx, cy = w // 2, h // 2
        val -= (abs(nx - cx) + abs(ny - cy)) * 0.1

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]