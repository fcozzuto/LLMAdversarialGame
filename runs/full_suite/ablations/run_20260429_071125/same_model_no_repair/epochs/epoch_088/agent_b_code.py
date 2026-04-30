def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            r = (int(p[0]), int(p[1]))
            if r not in obstacles:
                resources.append(r)
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    obs_list = list(obstacles)

    best_move = (0, 0)
    best_score = None
    opp_is_close = cheb(sx, sy, ox, oy) <= 1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0.0

        # Avoid obstacles: prefer staying farther from nearest obstacle cell
        if obs_list:
            dmin = 999
            for ax, ay in obs_list:
                d = cheb(nx, ny, ax, ay)
                if d < dmin:
                    dmin = d
            score += (dmin - 1) * 0.5  # penalize being adjacent or on top (on top already prevented)

        # Target selection: maximize potential advantage over opponent across all resources
        best_adv = -1e9
        nearest_my = 999
        nearest_opp = 999
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = (opd - myd)
            if adv > best_adv:
                best_adv = adv
            if myd < nearest_my:
                nearest_my = myd
            if opd < nearest_opp:
                nearest_opp = opd

        # Primary: advantage on some resource (try to get ahead)
        score += best_adv * 2.2

        # Secondary: if opponent is close, push to resources that reduce both distance & lead
        score += (nearest_opp - nearest_my) * (1.4 if opp_is_close else 1.0)

        # Tertiary: encourage progress (prefer smaller distance to best resource)
        score += -nearest_my * (0.18 if opp_is_close else 0.12)

        # Safety: if moving makes us closer to opponent than they are (possible contest), slightly discourage
        if cheb(nx, ny, ox, oy) < cheb(sx, sy, ox, oy):
            score -= 0.3

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]