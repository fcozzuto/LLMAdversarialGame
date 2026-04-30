def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    occ = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                occ.add((px, py))

    resources = []
    for p in (observation.get("resources", []) or []):
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in occ:
                resources.append((rx, ry))
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in occ

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) + abs(dy)

    if not resources:
        # fallback: move to increase distance from opponent and stay safe
        best_s, best = -10**18, (0, 0)
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            score = dist(nx, ny, ox, oy)
            if score > best_s:
                best_s, best = score, (dx, dy)
        return [best[0], best[1]]

    # choose resource where we have the largest advantage (closer than opponent)
    best_res = resources[0]
    best_adv = -10**18
    for rx, ry in resources:
        ds = dist(x, y, rx, ry)
        do = dist(ox, oy, rx, ry)
        adv = (do - ds) * 100 - ds
        if adv > best_adv:
            best_adv, best_res = adv, (rx, ry)

    rx, ry = best_res
    # opponent threat override: if they are very close to some resource, contest it if we can match
    threat = None
    threat_do = 10**9
    for tx, ty in resources:
        do = dist(ox, oy, tx, ty)
        if do < threat_do:
            threat_do, threat = do, (tx, ty)
    if threat is not None:
        tx, ty = threat
        if threat_do <= 2:
            ds_t = dist(x, y, tx, ty)
            if ds_t <= threat_do + 1:  # we can contest
                rx, ry = tx, ty

    # pick move that improves our distance to target; add repulsion from obstacles and opponent
    best_score, best_move = -10**18, (0, 0)
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        d_self = dist(nx, ny, rx, ry)
        d_opp = dist(nx, ny, ox, oy)

        # obstacle proximity penalty (prefer staying away from obstacles)
        near_obs = 0
        for ox2, oy2 in occ:
            if abs(nx - ox2) <= 1 and abs(ny - oy2) <= 1:
                near_obs += 1

        score = (-d_self) * 50 + (d_opp) * 2 - near_obs * 5 + (0 if (nx, ny) == (rx, ry) else -1)
        if score > best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]