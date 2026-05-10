def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # Pick a target where we have biggest distance advantage over the opponent.
    best_tx, best_ty = resources[0]
    best_adv = man(sx, sy, best_tx, best_ty) - man(ox, oy, best_tx, best_ty)
    best_sd = man(sx, sy, best_tx, best_ty)
    for rx, ry in resources[1:]:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = sd - od
        if adv < best_adv or (adv == best_adv and sd < best_sd) or (adv == best_adv and sd == best_sd and (rx, ry) < (best_tx, best_ty)):
            best_adv, best_sd, best_tx, best_ty = adv, sd, rx, ry

    def greedy_opp_step(apx, apy):
        # Opponent nearest resource; obstacle-aware one step toward it.
        tx, ty = resources[0]
        bestd = man(apx, apy, tx, ty)
        for rx, ry in resources[1:]:
            d = man(apx, apy, rx, ry)
            if d < bestd:
                bestd, tx, ty = d, rx, ry
        best = (apx, apy, 10**9)
        for mdx, mdy in moves:
            nx, ny = apx + mdx, apy + mdy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < best[2]:
                best = (nx, ny, d)
        return best[0], best[1]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        if not legal(nsx, nsy):
            continue

        nosx, nosy = greedy_opp_step(ox, oy)

        # Simulate immediate collection value heuristics.
        gain = 0
        if (nsx, nsy) in {(rx, ry) for rx, ry in resources}:
            gain += 1000
        if (nosx, nosy) in {(rx, ry) for rx, ry in resources}:
            gain -= 1200

        # Primary objective: minimize our distance to our chosen target while keeping advantage over opponent.
        d_self = man(nsx, nsy, best_tx, best_ty)
        d_opp = man(nosx, nosy, best_tx, best_ty)
        val = gain + (d_opp - d_self) * 50 - d_self

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]