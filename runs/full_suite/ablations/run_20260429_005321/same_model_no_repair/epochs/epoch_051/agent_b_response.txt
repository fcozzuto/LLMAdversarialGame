def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation["grid_width"]
    gh = observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp_move(dx, dy):
        if dx < -1: dx = -1
        if dx > 1: dx = 1
        if dy < -1: dy = -1
        if dy > 1: dy = 1
        return dx, dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Target is either our best "win race" resource, else the resource opponent is most likely to take next.
    best_win = None
    best_win_key = (-10**18, -10**18)
    best_threat = None
    best_threat_key = (-10**18, -10**18)
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = king_dist(sx, sy, rx, ry)
        od = king_dist(ox, oy, rx, ry)
        adv = od - sd  # >0 means we are closer
        # Win-race candidate: maximize advantage, then prefer closer than opponent.
        k1 = (adv, -sd)
        if k1 > best_win_key:
            best_win_key = k1
            best_win = (rx, ry)
        # Threat: opponent can take soonest; maximize negative of opponent distance.
        k2 = (-od, -sd)
        if k2 > best_threat_key:
            best_threat_key = k2
            best_threat = (rx, ry)

    # If we can beat at least one resource, race it; otherwise intercept the top threat.
    rx, ry = best_win if best_win_key[0] > 0 else best_threat

    # Decide also whether to "shadow" opponent when very close to threat completion.
    opp_to = king_dist(ox, oy, rx, ry)
    shadow = (best_win_key[0] <= 0 and opp_to <= 2)

    # Evaluate all legal moves by resulting advantage + safety + obstacle pressure + optional shadow.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obstacles:
            continue

        # Main: improvement in race metric toward chosen target.
        sd2 = king_dist(nx, ny, rx, ry)
        od2 = king_dist(ox, oy, rx, ry)
        adv2 = od2 - sd2

        # Secondary: avoid moves that make us worse off relative to other resources.
        near_pen = 0
        for j in resources:
            if j == (rx, ry):
                continue
            jx, jy = j
            if (jx, jy) in obstacles:
                continue
            # if we step into a spot where opponent is much closer to some other resource, penalize
            sdist = king_dist(nx, ny, jx, jy)
            odist = king_dist(ox, oy, jx, jy)
            near_pen += max(0, (odist - sdist) - 1)  # only punish when opponent edge is meaningful

        # Safety: steer away from obstacles indirectly by preferring squares with fewer blocked neighbors.
        blocked_neighbors = 0
        for mx, my in moves:
            tx, ty = nx + mx, ny + my
            if 0 <= tx < gw and 0 <= ty < gh and (tx, ty) in obstacles:
                blocked_neighbors += 1

        # Shadow opponent: when they are about to grab threat, prioritize decreasing our distance to their position.
        shadow_term = 0
        if shadow:
            shadow_term = king_dist(nx, ny, ox, oy)

        # If we can reach the target immediately, strongly prefer.
        reach_bonus = 0
        if sd2 == 0:
            reach_bonus = 10**6
        elif sd2 == 1 and king_dist(ox, oy, rx, ry) >= 2:
            reach_bonus = 5000

        val = (adv2 * 350 - sd2 * 10 + reach_bonus) - near_pen * 25 - blocked_neighbors * 8
        if shadow:
            # minimize distance to opponent while they are racing the target
            val -= shadow_term * 80