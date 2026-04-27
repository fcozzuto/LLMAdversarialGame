def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = (w - 1) - ox, (h - 1) - oy
        best = [0, 0, -10**9]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            score = cheb(nx, ny, tx, ty) * (-1) + cheb(nx, ny, ox, oy) * 0.01
            if score > best[2]:
                best = [dx, dy, score]
        return [best[0], best[1]]

    # Target resource by maximizing arrival advantage: d_op - d_me (higher means we should get it first)
    best_rx, best_ry = resources[0]
    best_adv = -10**9
    best_dop = -10**9
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        adv = d_op - d_me
        if adv > best_adv or (adv == best_adv and d_op > best_dop):
            best_adv, best_dop = adv, d_op
            best_rx, best_ry = rx, ry

    # One-step move: maximize new advantage for the same target; if tied, keep away from opponent.
    best_dx, best_dy = 0, 0
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        new_adv = cheb(nx, ny, best_rx, best_ry) * (-1) + cheb(ox, oy, best_rx, best_ry)
        # Discourage letting opponent be strictly closer to the target than we are after our move
        opp_to_target = cheb(ox, oy, best_rx, best_ry)
        me_to_target = cheb(nx, ny, best_rx, best_ry)
        penalty = 0
        if opp_to_target < me_to_target:
            penalty = (me_to_target - opp_to_target) * 10
        val = new_adv - penalty + cheb(nx, ny, ox, oy) * 0.001
        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]