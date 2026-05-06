def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_list.append((r[0], r[1]))
    if not res_list:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -(abs(nx - tx) + abs(ny - ty)) - (0 if (nx == sx and ny == sy) else 0)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose the most "contestable" resource (we are closer than opponent), then move to improve it.
    best_target = None
    best_tval = 10**18
    for rx, ry in res_list:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Prefer resources we can likely reach first; penalize those opponent is much closer to.
        tval = sd - 0.9 * od
        # Small bias towards nearer targets to avoid wandering.
        tval += 0.05 * sd
        if tval < best_tval or (tval == best_tval and (rx, ry) < best_target):
            best_tval = tval
            best_target = (rx, ry)

    rx, ry = best_target
    on_res_now = (sx == rx and sy == ry)

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd_next = md(nx, ny, rx, ry)
        od_to_res = md(ox, oy, rx, ry)
        # Higher is better:
        # - reduce our distance to contested target
        # - increase our advantage over opponent
        # - strong incentive to step onto any resource (not just target)
        step_resource_bonus = 0
        if any(nx == ar and ny == br for ar, br in res_list):
            step_resource_bonus = 1000
        # Discourage moving farther if not needed
        delta_self = sd_next - md(sx, sy, rx, ry)

        score = step_resource_bonus
        score += 50 * (od_to_res - sd_next)  # win the race
        score += -2 * sd_next
        score += -3 * delta_self
        if on_res_now and dx == 0 and dy == 0:
            score += 5  # tolerate staying if already on resource
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move