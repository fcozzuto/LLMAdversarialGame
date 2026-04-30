def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    valid_res = [(x, y) for x, y in resources if inb(x, y) and (x, y) not in obs]
    if not valid_res:
        return [0, 0]

    # Pick our best target if we can lead; otherwise pick opponent's nearest target to intercept.
    best_adv = None
    our_target = valid_res[0]
    for tx, ty in valid_res:
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        adv = do - ds
        if best_adv is None or adv > best_adv or (adv == best_adv and (ds, tx, ty) < (man(sx, sy, our_target[0], our_target[1]), our_target[0], our_target[1])):
            best_adv = adv
            our_target = (tx, ty)

    opp_best = None
    opp_target = valid_res[0]
    for tx, ty in valid_res:
        do = man(ox, oy, tx, ty)
        if opp_best is None or do < opp_best or (do == opp_best and (tx, ty) < opp_target):
            opp_best = do
            opp_target = (tx, ty)

    intercept_mode = best_adv <= 0

    # Greedy one-step lookahead with obstacle and separation considerations.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dn_our = man(nx, ny, our_target[0], our_target[1])
        dn_opp = man(nx, ny, opp_target[0], opp_target[1])
        dn_sep = man(nx, ny, ox, oy)

        if intercept_mode:
            # Intercept: prioritize getting closer to opponent's target while keeping some separation.
            score = (-dn_opp * 4) + (dn_sep * 0.5) - (dn_our * 1.0)
        else:
            # Lead: prioritize our target, discourage helping the opponent by staying near resources they value.
            dn_opp_to_our = man(ox, oy, our_target[0], our_target[1])
            help_pen = (dn_opp_to_our - man(ox, oy, opp_target[0], opp_target[1])) *