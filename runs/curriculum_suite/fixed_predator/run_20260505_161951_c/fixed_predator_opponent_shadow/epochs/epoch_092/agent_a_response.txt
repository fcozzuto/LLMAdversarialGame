def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = md(nx, ny, tx, ty)
            key = (d, md(nx, ny, ox, oy))
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    opp_to_res = [md(ox, oy, rx, ry) for rx, ry in resources]
    best_move = None
    best_key = None

    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        self_to_res = [md(nx, ny, rx, ry) for rx, ry in resources]
        self_min = min(self_to_res)
        opp_min = min(opp_to_res)
        # Maximize how much closer we are than the opponent to the remaining resources
        adv = opp_min - self_min
        nearest_resource = None
        nearest_dist = None
        for i, (rx, ry) in enumerate(resources):
            d = self_to_res[i]
            if nearest_dist is None or d < nearest_dist or (d == nearest_dist and (rx, ry) < nearest_resource):
                nearest_dist = d
                nearest_resource = (rx, ry)
        # Prefer higher advantage, then smaller self_min, then deterministic tie-breaker
        key = (-adv, self_min, nearest_resource[0], nearest_resource[1], dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]