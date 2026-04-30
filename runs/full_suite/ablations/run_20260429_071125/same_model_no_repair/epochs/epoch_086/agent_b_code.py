def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            r = (int(p[0]), int(p[1]))
            if r not in obstacles:
                resources.append(r)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def pick_target():
        best = None
        best_adv = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive => we are closer
            if best is None:
                best = (rx, ry)
                best_adv = adv
            else:
                if adv > best_adv:
                    best, best_adv = (rx, ry), adv
                elif adv == best_adv:
                    # tie-break: prefer nearer resource for us, then deterministic coordinate
                    cs = sd
                    bs = cheb(sx, sy, best[0], best[1])
                    if cs < bs or (cs == bs and (rx, ry) < best):
                        best = (rx, ry)
        # If we are not actually advantaged, pivot to closest resource for us
        if best_adv is not None and best_adv < 0:
            best = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
        return best

    tx, ty = pick_target()

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_opp_d = cheb(sx, sy, ox, oy)
    cur_me_d = cheb(sx, sy, tx, ty)
    lose = cheb(ox, oy, tx, ty) <= cur_me_d  # opponent is at least as close

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        opp_d = cheb(nx, ny, ox, oy)

        # Core: reduce distance to target.
        val = nd * 10

        # If losing on this target, avoid giving the opponent an even easier race.
        if lose:
            # prefer staying safer from opponent (not getting closer)
            val += (cur_opp_d - opp_d) * 3  # if opp_d decreases => penalty

        # If we are advantaged, slightly encourage convergence and discourage widening the race.
        else:
            my_adv = cheb(ox, oy, tx, ty) - nd
            val += -my_adv  # larger my_adv => smaller val

        # Tie-break deterministic by move ordering
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]