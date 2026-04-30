def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        best = (0, 0, -10**9)
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, ox, oy)
            v = d  # just drift away
            if v > best[2] or (v == best[2] and (dx, dy) < (best[0], best[1])):
                best = (dx, dy, v)
        return [best[0], best[1]]

    rem = observation.get("remaining_resource_count", len(resources))
    # pick a single best target resource by distance advantage
    best_target = None
    best_adv = -10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        # obstacle friction near the resource
        near_obs = 0
        for bx, by in blocked:
            if cheb(rx, ry, bx, by) <= 1:
                near_obs += 1
        adv -= 0.15 * near_obs
        # late game: focus on closer wins (less patience)
        if rem <= len(resources) // 3:
            adv += 0.05 * (-(sd))
        if adv > best_adv or (adv == best_adv and (rx, ry) < (best_target[0], best_target[1]) if best_target else False):
            best_adv = adv
            best_target = (rx, ry)
    tx, ty = best_target

    # evaluate immediate moves: maximize winning-chance proxy
    best = (0, 0, -10**18)
    for dx, dy, nx, ny in legal:
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        self_dist_now = cheb(nx, ny, sx, sy)
        opp_to_self = cheb(nx, ny, ox, oy)
        # obstacle wedging penalty
        wed = 0
        for bx, by in blocked:
            if cheb(nx, ny, bx, by) <= 1:
                wed += 1
        v = (opp_d - self_d) - 0.12 * wed + 0.02 * (opp_to_self > 1) - 0.01 * self_dist_now
        # prefer moving closer to target
        v += 0.03 * (cheb(sx, sy, tx, ty) - self_d)
        if v > best[2] or (v == best[2] and (dx, dy) < (best[0], best[1])):
            best = (dx, dy, v)
    return [best[0], best[1]]