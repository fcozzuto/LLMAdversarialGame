def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Materially different from "center build": favor contest advantage (opponent race),
        # but only for resources we can reach reasonably soon.
        best_res = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive: we are closer to this resource than opponent
            center_bias = abs(rx - cx) + abs(ry - cy)
            # Encourage stealing contested nodes; still prefer nearest if no contest.
            val = adv * 8 - ds - center_bias * 0.01
            # Slight penalty for moving away if already behind.
            if adv < 0:
                val -= (-adv) * 2
            if val > best_res:
                best_res = val

        # Keep some pressure: if we can't get contest, at least move toward nearest resource
        if best_res < -10**17:
            nearest = min(cheb(nx, ny, rx, ry) for (rx, ry) in resources)
            best_res = -nearest

        # Secondary tie-break: reduce our distance to opponent only if it helps (contest)
        opp_dist = cheb(nx, ny, ox, oy)
        val2 = best_res - opp_dist * 0.02
        if val2 > best_val:
            best_val = val2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]