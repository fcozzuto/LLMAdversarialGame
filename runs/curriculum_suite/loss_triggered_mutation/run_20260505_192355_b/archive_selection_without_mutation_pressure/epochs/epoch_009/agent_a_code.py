def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs_list)

    resources = observation.get("resources") or []
    res = [tuple(r) for r in resources] if resources else []

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        d_op = man(nx, ny, ox, oy)
        score = 0

        if res:
            md = 10**9
            for rx, ry in res:
                d = man(nx, ny, rx, ry)
                if d < md:
                    md = d
            score += 1000 / (1 + md)
        score += 5 * d_op

        rcount = observation.get("remaining_resource_count")
        if rcount is not None:
            try:
                if int(rcount) <= 1:
                    score -= 10 * d_op
            except:
                pass

        if score > bestv:
            bestv = score
            best = [dx, dy]

    if bestv == -10**18:
        return [0, 0]
    return best