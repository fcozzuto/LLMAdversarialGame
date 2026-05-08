def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles)

    # If we're on a resource already, stay (should be harmless).
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = [dx, dy]
        return best

    # Pick move that maximizes expected "first to resource" advantage.
    # Tie-break deterministically by move order.
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
            continue

        # Immediate collection if landing on a resource.
        collect = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                collect = 1
                break

        # Find best resource to pursue: maximize (opp_dist - self_dist), also prefer closer net.
        best_adv = -10**9
        best_self = 10**9
        best_opp = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > best_adv or (adv == best_adv and ds < best_self):
                best_adv = adv
                best_self = ds
                best_opp = do

        # Small penalty if opponent is already very close to the same target area.
        # This biases to contest only when we can likely arrive first.
        close_pen = 0
        if best_opp <= 1:
            close_pen = 2

        # Combine: collecting > strongest advantage > prefer nearer target.
        obj = (1000 if collect else 0) + best_adv * 10 - best_self - close_pen
        moves.append((obj, dx, dy))

    if not moves:
        return [0, 0]

    moves.sort(key=lambda t: (-t[0], dirs.index((t[1], t[2])) if (t[1], t[2]) in dirs else 0))
    # Deterministic final pick: first in sorted list.
    _, dx, dy = moves[0]
    return [int(dx), int(dy)]