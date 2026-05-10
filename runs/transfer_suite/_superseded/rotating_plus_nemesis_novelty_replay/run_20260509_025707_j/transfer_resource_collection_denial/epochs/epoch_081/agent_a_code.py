def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0), (1, 0),
            (-1, 1),  (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    tr = observation.get("turns_remaining", 0)
    opp_to = {}
    for rx, ry in resources:
        opp_to[(rx, ry)] = d_cheb(ox, oy, rx, ry)

    best = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = 0
        worst_adv = 10**9
        best_adv = -10**9
        best_self = 10**9
        target_touch = False

        for (rx, ry) in resources:
            self_d = d_cheb(nx, ny, rx, ry)
            opp_d = opp_to[(rx, ry)]
            adv = opp_d - self_d  # positive means we get there first
            if adv < worst_adv:
                worst_adv = adv
            if adv > best_adv:
                best_adv = adv
            if self_d < best_self:
                best_self = self_d
            if self_d == 0:
                target_touch = True

        # Emphasize taking resources before opponent (main), but also avoid moves
        # that give the opponent many chances (via worst_adv).
        # Late game: prioritize immediate pickup strongly.
        pickup_boost = 80 if target_touch else 0
        time_boost = (0 if tr >= 20 else 8 if best_adv > 0 else 0)
        val = (best_adv * 30) + (worst_adv * 4) - (best_self * 2) + pickup_boost + time_boost
        if val > best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]