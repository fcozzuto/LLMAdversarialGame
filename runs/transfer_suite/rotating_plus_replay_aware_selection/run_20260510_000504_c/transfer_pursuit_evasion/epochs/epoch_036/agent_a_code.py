def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obs = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except:
            pass

    res = observation.get("resources", None)
    resources = []
    if isinstance(res, list):
        for p in res:
            try:
                x, y = p
                resources.append((int(x), int(y)))
            except:
                pass
    if "remaining_resource_count" in observation and not resources:
        if observation.get("remaining_resource_count", 0):
            resources = []

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    res_exist = bool(resources)

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        opp_dx, opp_dy = nx - ox, ny - oy
        d_opp2 = opp_dx * opp_dx + opp_dy * opp_dy

        if res_exist:
            md2 = None
            for rx, ry in resources:
                tx, ty = nx - rx, ny - ry
                v = tx * tx + ty * ty
                if md2 is None or v < md2:
                    md2 = v
            score = -md2 + d_opp2 // 4
        else:
            score = d_opp2

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best