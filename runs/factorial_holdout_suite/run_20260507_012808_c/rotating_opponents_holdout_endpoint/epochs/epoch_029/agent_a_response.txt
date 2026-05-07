def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Evaluate best resource from the next position, but penalize moving away from "current race"
        # Race proxy: opponent's closest resource (under chebyshev distance).
        opp_best = None
        opp_best_d = None
        for rx, ry in resources:
            d = cheb(ox, oy, rx, ry)
            if opp_best_d is None or d < opp_best_d:
                opp_best_d = d
                opp_best = (rx, ry)
        race_rx, race_ry = opp_best

        val = 0
        # Primary: maximize advantage over opponent for the next resource.
        # Secondary: if tied, prefer resources closer to us from nx,ny.
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > 0:
                val = max(val, adv * 100 - ds)
            else:
                val = max(val, adv * 10 - ds)

        # Add a deterministic "chase the race" term to change behavior vs pure target-hunting:
        # if opponent is about to secure the race resource, we prioritize moving closer to it.
        ds_race = cheb(nx, ny, race_rx, race_ry)
        val += (opp_best_d - ds_race) * 7

        # Small preference to reduce distance to opponent when no clear advantage:
        if val <= 0:
            val += (cheb(ox, oy, sx, sy) - cheb(ox, oy, nx, ny)) * 2

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]