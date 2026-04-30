def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_r = resources[0]
        best_gain = -10**9
        for r in resources:
            rx, ry = r
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gain = do - ds
            if gain > best_gain:
                best_gain = gain
                best_r = r
        rx, ry = best_r

        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            ds_next = cheb(nx, ny, rx, ry)
            do_now = cheb(ox, oy, rx, ry)
            block = cheb(nx, ny, ox, oy)  # prefer staying away from opponent
            val = (do_now - ds_next) * 10 - ds_next - block * 0.05
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: drift toward opponent's side while keeping distance
    tx, ty = (w - 1, h - 1) if ox + oy < sx + sy else (0, 0)
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist_to_target = cheb(nx, ny, tx, ty)
        dist_to_opp = cheb(nx, ny, ox, oy)
        val = dist_to_opp * 0.2 - dist_to_target
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]