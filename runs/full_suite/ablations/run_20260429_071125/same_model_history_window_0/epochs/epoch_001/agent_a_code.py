def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    rem = observation.get("remaining_resource_count", len(resources))

    deltas = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target():
        if not resources:
            return None
        # Deterministic tie-break by coordinates
        best = None
        best_d = 10**9
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < best_d or (d == best_d and (rx, ry) < best):
                best_d = d
                best = (rx, ry)
        return best

    target = best_target()
    if target is None:
        # No resources: move toward opponent if possible
        tx, ty = ox, oy
    else:
        tx, ty = target

    # If resources are scarce, bias slightly toward opponent to contest
    if rem <= 2:
        opp_bias = 1
    else:
        opp_bias = 0

    best_move = (0, 0)
    best_score = 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Score: prefer nearing target; discourage approaching blocked region; optional contest
        d_to_target = cheb(nx, ny, tx, ty)
        score = d_to_target * 1000 + (1 if opp_bias and cheb(nx, ny, ox, oy) < cheb(sx, sy, ox, oy) else 0)
        # Additional deterministic nudge toward lowering distance to nearest resource when target is awkward
        if resources:
            md = 10**9
            for rx, ry in resources:
                dd = cheb(nx, ny, rx, ry)
                if dd < md:
                    md = dd
            score += md
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves invalid (surrounded by obstacles), stay
    return [int(best_move[0]), int(best_move[1])]