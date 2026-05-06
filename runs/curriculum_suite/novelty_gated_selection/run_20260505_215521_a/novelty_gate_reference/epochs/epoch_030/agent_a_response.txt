def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    resources = observation.get("resources", []) or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                res_list.append((x, y))
    if not res_list:
        return [0, 0]

    deltas = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def risk(x, y):
        rr = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs_set:
                    rr += 2 if (ax == 0 or ay == 0) else 1
        return rr

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            nx, ny = sx, sy
        opp_d = md((nx, ny), (ox, oy))
        nearest_d = min(md((nx, ny), r) for r in res_list)
        nearest_res = min(res_list, key=lambda r: md((nx, ny), r))
        center_bias = -md((nx, ny), (w // 2, h // 2)) * 0.02
        block_bias = 0.0
        if ox != nx or oy != ny:
            # encourage moving to interfere with opponent's likely approach direction
            block_bias = 0.08 * (1 if md((ox, oy), nearest_res) > md((nx, ny), nearest_res) else -1)
        score = -nearest_d + 0.12 * opp_d - 0.35 * risk(nx, ny) + center_bias + block_bias
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
    return best