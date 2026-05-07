def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    def pt(p):
        if isinstance(p, dict):
            if "position" in p:
                p = p["position"]
            return int(p.get("x", p[0])), int(p.get("y", p[1]))
        return int(p[0]), int(p[1])

    def man(a, b, x, y):
        dx = a - x
        if dx < 0: dx = -dx
        dy = b - y
        if dy < 0: dy = -dy
        return dx + dy

    # Prioritize resources where we are closer than opponent, then maximize distance margin.
    best = None
    best_val = None
    for r in resources:
        rx, ry = pt(r)
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Strongly prefer "we beat opponent on distance"
        self_closer = 1 if sd < od else 0
        tie_break = -sd  # prefer smaller self distance when tie
        val = (self_closer, od - sd, tie_break, - (sd + od))
        if best_val is None or val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If already on target, try to stay; still deterministic.
    return [dx, dy]