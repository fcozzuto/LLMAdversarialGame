def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a dynamic frontier: prefer resources we can reach not later than opponent, else pick the earliest steal.
    best_targets = []
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # primary: we want ds <= do; secondary: maximize (do-ds); tertiary: minimize do
        priority = 0
        if ds <= do:
            priority = 1
        best_targets.append((priority, do - ds, -do, rx, ry, ds, do))
    best_targets.sort(reverse=True)
    top = best_targets[: min(6, len(best_targets))]

    # Evaluate candidate moves by how they affect "win chances" on these targets.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            val = 0
            # Encourage moving toward reachable targets, and discourage letting opponent be earlier.
            for _, _, _, rx, ry, _, _ in top:
                ns = cheb(nx, ny, rx, ry)
                no = cheb(ox, oy, rx, ry)
                # If we are earlier, big reward; if later, big penalty with softer scaling.
                diff = no - ns
                if ns <= no:
                    val += 30 + 10 * diff - ns
                else:
                    val += -25 + 3 * diff - ns * 0.5
            # Light tie-break: keep away from opponent a bit (helps against sweep behavior).
            val += 0.1 * cheb(nx, ny, ox, oy)
            candidates.append((val, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0], -abs(t[1]) - abs(t[2])), reverse=True)
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]