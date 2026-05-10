def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_ob_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            nx = x + dx
            if nx < 0 or nx >= w:
                continue
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ny = y + dy
                if 0 <= ny < h and (nx, ny) in obs:
                    pen += 1
        return pen

    valid_resources = []
    for x, y in resources:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            valid_resources.append((x, y))
    if not valid_resources:
        return [0, 0]

    best_score = -10**18
    best_move = [0, 0]

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            continue

        # choose target that we can reach earlier than opponent, otherwise the most winnable
        local_best = -10**18
        for rx, ry in valid_resources:
            sd = cheb_dist(nx, ny, rx, ry)
            od = cheb_dist(ox, oy, rx, ry)
            # Prefer resources where (od - sd) is large; then prefer smaller sd
            # Minor preference to nearer to current position to reduce dithering
            s = (od - sd) * 10 - sd - adj_ob_pen(nx, ny) * 0.3
            if s > local_best:
                local_best = s

        # Small deterministic bias: keep moving unless equal
        move_bias = -(abs(dxm) + abs(dym)) * 0.01
        val = local_best + move_bias
        if val > best_score:
            best_score = val
            best_move = [dxm, dym]

    return best_move