def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obstacles}
    resources = observation.get("resources") or []

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_score = None

    if not resources:
        # Drift to reduce opponent's reachable advantage: go toward opponent-opposite corner if possible.
        tx = 0 if sx > w - 1 - ox else w - 1
        ty = 0 if sy > h - 1 - oy else h - 1
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            score = -man(nx, ny, tx, ty) + 0.01 * (-man(nx, ny, ox, oy))
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    # If multiple resources, denier-style: pick move that maximizes our (opp_dist - self_dist) for the best resource.
    # Deterministic tie-breaking: higher capture, then larger advantage, then lower our distance, then lexicographic move order.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        capture = 0
        best_adv = -10**9
        best_self_d = 10**9
        for rx, ry in resources:
            if rx == nx and ry == ny:
                capture = 1
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - self_d
            if adv > best_adv or (adv == best_adv and self_d < best_self_d):
                best_adv = adv
                best_self_d = self_d

        # Encourage cleaning up: big weight on capture and advantage; slight penalty for absolute distance.
        score = (100000 if capture else 0) + best_adv * 100 - best_self_d
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move