def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obs_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obs:
                    pen += 1
        return pen

    def best_resource_for_cell(x, y):
        best = None
        bestv = -10**18
        for rx, ry in res:
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we arrive sooner; then shorter distance.
            v = (od - sd) * 1000 - sd * 3 - (rx == x and ry == y) * 0
            if v > bestv:
                bestv = v
                best = (rx, ry, sd, od)
        return best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Tie-break deterministically by fixed move order.
    best_move = (0, 0)
    best_score = -10**18

    # Opponent tends to sweep; reduce letting them take a close line by prioritizing
    # resources aligned near our row/col when roughly competitive.
    sx_center = sx - (w // 2)
    sy_center = sy - (h // 2)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            # Engine will keep us in place if invalid; treat as strongly worse unless no options.
            nx, ny = sx, sy

        br = best_resource_for_cell(nx, ny)
        rx, ry, sd, od = br

        # Additional shaping: avoid stepping next to obstacles; mild preference to reduce distance to chosen resource.
        center_pen = abs(nx - (w // 2)) + abs(ny - (h // 2))
        align_bonus = 0
        if rx == nx or ry == ny:
            align_bonus = 25  # helps vs row/column sweep patterns

        score = (od - sd) * 1000 - sd * 4 - adj_obs_pen(nx, ny) * 10 - center_pen * 0.5 + align_bonus

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]