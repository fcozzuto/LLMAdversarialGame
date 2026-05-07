def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp_moves(nx, ny):
        if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs:
            return True
        return False

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Deterministic target selection and move scoring: maximize "race" advantage
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_moves(nx, ny):
            continue
        # Avoid letting opponent get too close: minimize opponent proximity after move
        opp_close = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        # Race value: how much closer we are than opponent to the same target
        race_best = -10**18
        goal_pref = 0
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - self_d
            if adv > race_best:
                race_best = adv
                goal_pref = self_d
            elif adv == race_best and self_d < goal_pref:
                goal_pref = self_d
        # Tie-break: also prefer moves that reduce distance to the "most contested" resource we can still reach well
        contested = max(resources, key=lambda t: (cheb(ox, oy, t[0], t[1]) - cheb(sx, sy, t[0], t[1]), -cheb(sx, sy, t[0], t[1])))
        cont_d = cheb(nx, ny, contested[0], contested[1])
        opp_prox = cheb(nx, ny, ox, oy)
        val = (race_best * 1000) - cont_d - opp_prox - (opp_close * 0.1)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]