def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    res = observation.get("resources") or []
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Opponent archetype: sweep_rows -> likely favors current row, so de-prioritize ry==oy.
        row_bias = -2 if ry == oy else 1
        # Main objective: be closer than opponent; tie-break by being closer to the goal.
        score = (do - ds) + row_bias * 3 - ds * 0.01
        if best is None or score > best[0]:
            best = (score, rx, ry)

    _, tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [dx, dy]