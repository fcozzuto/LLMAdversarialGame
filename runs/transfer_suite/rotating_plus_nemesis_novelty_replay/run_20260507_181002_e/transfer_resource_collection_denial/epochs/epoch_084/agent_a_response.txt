def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_key = (-10**18, 10**9, -10**9, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0

        # For this step, pick the resource where we gain most distance advantage.
        # Key: max (opp_dist - self_dist), then min self_dist, then max opp_dist.
        local_best = (-10**18, 10**9, -10**9)
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            cand = (adv, -sd, od)  # adv max; then -sd max => sd min; then od max
            if (cand[0], cand[1], cand[2]) > (local_best[0], -local_best[1], local_best[2]):
                local_best = (adv, sd, od)

        # Secondary tie-break: prefer moving toward the board center slightly (robustness).
        centerx, centery = (w - 1) / 2.0, (h - 1) / 2.0
        center_score = -abs(nx - centerx) - abs(ny - centery)

        key = (local_best[0], -local_best[1], local_best[2], center_score)
        if key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]