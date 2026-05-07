def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_resource_score(px, py):
        best = None
        for rx, ry in resources:
            sd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we have a distance advantage; break ties toward being closer.
            s = (od - sd, -sd, -rx, -ry)
            if best is None or s > best[0]:
                best = (s, sd)
        return best[0][0], best[0][1]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (None, None, None)
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        adv, negsd = best_resource_score(nx, ny)
        # Small deterministic bias to reduce dithering: prefer staying or moving toward increasing x, then y.
        tie_bias = (0 if (nx == sx and ny == sy) else 1, nx, ny)
        score = (adv, negsd, tie_bias[0], tie_bias[1], tie_bias[2])
        if best_move[0] is None or score > best_move[0]:
            best_move = (score, dx, dy)

    return [int(best_move[1]), int(best_move[2])]