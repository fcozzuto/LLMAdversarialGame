def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {tuple(p) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def cand_steps(x, y):
        return [
            (0, 0), (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

    # Pick target: maximize distance advantage (opponent farther)
    best_r = resources[0]
    best_adv = -10**18
    for rx, ry in resources:
        myd = d2(sx, sy, rx, ry)
        opd = d2(ox, oy, rx, ry)
        adv = opd - myd  # larger => we are closer
        if adv > best_adv or (adv == best_adv and (rx, ry) < tuple(best_r)):
            best_adv = adv
            best_r = [rx, ry]
    tx, ty = best_r

    # Obstacle danger: penalize stepping onto/adjacent to obstacles
    obst_list = [tuple(p) for p in obstacles]
    def danger(x, y):
        if not obst_list:
            return 0
        mind = 10**9
        for px, py in obst_list:
            dd = d2(x, y, px, py)
            if dd < mind:
                mind = dd
        # if in same cell (should be avoided), or adjacent (8-neigh), heavy penalty
        if mind == 0:
            return 1e9
        if mind <= 2:
            return 10000 - mind
        return 0

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in cand_steps(sx, sy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue

        # Advance toward target and widen race advantage
        my_after = d2(nx, ny, tx, ty)
        opp_after = d2(ox, oy, tx, ty)
        # also consider stealing other resources implicitly via self progress: discourage moving away overall
        self_progress = d2(sx, sy, tx, ty) - my_after

        score = 2000 * (opp_after - my_after) + 10 * self_progress
        score -= danger(nx, ny)

        # If we're very close to target, prioritize capturing over further advantage
        if my_after <= 1:
            score += 1e6

        # Mild tie-break: deterministic ordering already from iteration, but ensure stability
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]