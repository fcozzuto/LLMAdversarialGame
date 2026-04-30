def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx >= dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None; bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            # keep away from opponent while preferring approach to the best corner
            d_opp = cheb(nx, ny, ox, oy)
            d_corner = min(cheb(nx, ny, cx, cy) for (cx, cy) in corners)
            v = 1.0 * d_opp - 0.05 * d_corner
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Relative-resource pressure: maximize (opp_dist - my_dist) toward the best resource,
    # with a small bias toward reducing my distance.
    best = (0, 0); bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best_r = -10**18
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # If I'm already on a resource, that's dominant.
            if d_my == 0:
                v = 10**9 + d_opp
            else:
                v = (d_opp - d_my) * 2.0 - 0.03 * d_my + 0.01 * d_opp
            if v > best_r:
                best_r = v
        # If multiple moves have same pressure, slightly prefer being closer overall to resources
        near_my = min(cheb(nx, ny, rx, ry) for (rx, ry) in resources)
        v = best_r - 0.002 * near_my
        if v > bestv:
            bestv = v; best = (dx, dy)
    return [best[0], best[1]]