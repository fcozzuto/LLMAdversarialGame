def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**18

    # If no resources, drift toward center.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    # Heuristic: choose move that maximizes (opp_dist - self_dist) to the most "stealable" resource.
    # Secondary: prefer smaller self distance and avoid moves that are closer to opponent's nearest resource.
    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        best_local = -10**18
        for rx, ry in resources:
            if not valid(rx, ry):
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach first (do - ds large), and in tie prefer shorter ds.
            val = (do - ds) * 100 - ds
            if val > best_local:
                best_local = val

        # Add small denier pressure: avoid moving toward positions where opponent is "too close"
        # to their closest resource (resource_denier-style).
        closest_opp = 10**9
        for rx, ry in resources:
            if not valid(rx, ry):
                continue
            dp = cheb(ox, oy, rx, ry)
            if dp < closest_opp:
                closest_opp = dp
        # If we step closer to opponent than to their closest resource, slightly reduce.
        closer_to_opp = cheb(nx, ny, ox, oy)
        opp_pen = -max(0, closest_opp - closer_to_opp) * 2

        total = best_local + opp_pen
        if best is None or total > best_val or (total == best_val and (nx, ny) < best):
            best_val = total
            best = (nx, ny)

    if best is None:
        return [0, 0]
    dxm = best[0] - sx
    dym = best[1] - sy
    if dxm < -1: dxm = -1
    if dxm > 1: dxm = 1
    if dym < -1: dym = -1
    if dym > 1: dym = 1
    return [int(dxm), int(dym)]